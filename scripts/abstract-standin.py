import os
import sys
import time
import yaml
import importlib

from h4h_msgs.msg import AbstractSignal, BatchedAbstractSignal

from commons.utils_lib import timeit

import commons.ros2_lib as rlib
import commons.h4h_lib as hlib


with open("config.yaml", 'r') as file:
    yaml_config = yaml.safe_load(file)

imports = dict()

def do_imports(yaml_config):
    for topic in yaml_config['topics']:
        pkg = importlib.import_module(topic['package'])

        print("Message:", topic['msg'])
        print("Topic:", topic['topic_name'])

        imports[topic['topic_name']] = vars(pkg)[topic['msg']]

class AbstractNode(hlib.H4HBase):
    def __init__(self):
        # set up parent
        super().__init__(name="AbstractController")
        self.logger.info(f"Started Init")

        # set up subcribers list
        self.subs = []
        self.callbacks = []

        # add publishers as new namespaces encountered
        self.publisher_map = {}

        # abstract signal message is imported as a class object, so we need to extract the dictionary
        self.abstract_signal_dict = vars(AbstractSignal)
        for topic in yaml_config['topics']:
            self.callbacks.append(self.SmartCallback(imports[topic['topic_name']], topic['msg_fields'], self.publisher_map, self.abstract_signal_dict, self.logger))

            # build node name
            node_name = topic['topic_name'] + "AbstractControllerSubscriber"

            # create subscriber and add to list
            sub = rlib.RosSubscriber(
                node_name=node_name,
                msg_type=imports[topic['topic_name']],
                rostopic=topic['topic_name'],
                callback=self.callbacks[-1].my_callback,
                namespace=self.namespace)
            self.subs.append(sub)
        self.logger.info(f"Finished Init")


    class SmartCallback:

        def __init__(self, current_import, msg_fields, publisher_map, abstract_signal_dict, logger):
            self.current_import = current_import
            self.msg_fields = msg_fields
            self.publisher_map = publisher_map
            self.abstract_signal_dict = abstract_signal_dict
            self.logger = logger

            # accumulator to generate BatchedAbstractSignal
            self.priority = 256
            self.msg_namespace = "MISSING ROS NAMESPACE"

            self.signal_list = []

            # build a map between enumerations and signals for easy lookup in the callback
            self.matched_map = dict()
            for field in self.msg_fields:
                if field['type'] == 'matched':
                    keys = field['mapping'].keys()
                    dict_import = vars(self.current_import)
                    for key in keys:
                        self.matched_map[dict_import[key]] = field['mapping'][key]

            print("Initialized SmartCallback for", self.current_import)

        # @timeit
        def my_callback(self, msg):
            self.logger.info(f"Received: {msg}")

            # reset the signal list
            self.signal_list = []

            # pull out the target namespace and the priority
            self.msg_namespace = msg.name
            self.priority = msg.priority

            # parse each of the fields in to a signal
            for field in self.msg_fields:
                try:
                    field_curr = getattr(msg, field['msg_field_name']) #field_curr is the value of that field from the message
                except KeyError:
                    self.logger.warning(f"Field \'{field['msg_field_name']}\' does not exist in message.")
                    continue

                # get field mapping
                mapping_curr = field['mapping']

                # interpret mapping based on field type
                # threshold or value case
                if field['type'] in ['threshold', 'value']:
                    # cast all values to list and check their lengths
                    # all mapping values should be of equal length, or length 1
                    mapping_curr = {k: v if isinstance(v, list) else [v] for k, v in mapping_curr.items()}
                    mapping_lens = [len(v) for v in mapping_curr.values()]
                    mapping_lens_check = [True if (l ==1 or l == max(mapping_lens)) else False for l in mapping_lens]


                    # DEBUG DEBUG DEBUG
                    # print("Mapping_Lens:", mapping_lens)

                    assert all(mapping_lens_check), 'All mapping fields must be of the same length, or 1.'
                    assert len(mapping_curr['output']) == 1, 'Each mapping can only result in one output signal.'
                    assert (('output_index' not in mapping_curr) or len(mapping_curr['output_index']) == 1), 'Each mapping can only result in one output value.'

                    # check all conditions
                    satisfied_conditions = [False for i in range(max(mapping_lens))]
                    for i in range(max(mapping_lens)):

                        # if there's an index, index into the data structure
                        if "index" in mapping_curr:
                            mapping_index = mapping_curr['index'][i] if len(mapping_curr['index']) > 1 else mapping_curr['index'][0]
                            try:
                                field_value = field_curr[mapping_index]
                            except IndexError:
                                self.logger.warning(f"Field \'{field['msg_field_name']}\' does not have the index {mapping_index}")
                                continue
                        else:
                            field_value = field_curr

                        # check condition, based on each operator and value
                        mapping_operator = mapping_curr['operator'][i] if len(mapping_curr['operator']) > 1 else mapping_curr['operator'][0]
                        mapping_value = mapping_curr['value'][i] if len(mapping_curr['value']) > 1 else mapping_curr['value'][0]
                        if mapping_operator == 'gt':
                            if field_value > mapping_value:
                                satisfied_conditions[i] = True
                        elif mapping_operator == 'lt':
                            if field_value < mapping_value:
                                satisfied_conditions[i] = True
                        elif mapping_operator == 'eq':
                            if field_value == mapping_value:
                                satisfied_conditions[i] = True
                        elif mapping_operator == 'gte':
                            if field_value >= mapping_value:
                                satisfied_conditions[i] = True
                        elif mapping_operator == 'lte':
                            if field_value <= mapping_value:
                                satisfied_conditions[i] = True
                        elif mapping_operator == 'neq':
                            if field_value != mapping_value:
                                satisfied_conditions[i] = True
                        else:
                            self.logger.warning(f"Unknown operator \'{mapping_operator}\'")
                            continue

                    # get numerical value for enum and publish if all conditions are satisfied
                    if all(satisfied_conditions):
                        output_signal = self.abstract_signal_dict[mapping_curr['output'][0]]
                        # if threshold, only output signal
                        if field['type'] == 'threshold':
                            self.publish_output_signal(output_signal)
                        # otherwise (if value), output signal and value
                        elif field['type'] == 'value':
                            try:
                                if "output_index" in mapping_curr:
                                    output_index = mapping_curr['output_index'][0]
                                    output_value = field_curr[output_index]
                                else:
                                    output_value = field_curr
                            except IndexError:
                                self.logger.warning(f"Field \'{field['msg_field_name']}\' does not have the index {output_index}")
                                continue
                            self.publish_output_signal(output_signal, output_value)

                # matched case
                elif field['type'] == 'matched':
                    # retrieve string version of the signal from the matched map, then use it to retrieve the integer from AbstractSignal
                    try:
                        output_signal = self.abstract_signal_dict[self.matched_map[field_curr]]
                        self.publish_output_signal(output_signal)
                    except KeyError:
                        self.logger.warning("The received value is not defined in the configuration. No message will be published.")

                    # passthrough string actions
                elif field['type'] == "passthrough":
                    # generate an AbstractSignal.PASSTHROUGH message for each action
                    if hasattr(field_curr, '__iter__'):
                        # extract the paired values list
                        paired_list_name = field["mapping"]["paired_list"]
                        paired_list = getattr(msg, paired_list_name)

                        for action_index in range(len(field_curr)):
                            # extract value from paired list
                            action = field_curr[action_index]
                            output_value = paired_list[action_index]
                            self.publish_output_signal(AbstractSignal.PASSTHROUGH, output_value=output_value, output_passthrough=action)
                    else:
                        self.publish_output_signal(AbstractSignal.PASSTHROUGH, output_passthrough=field_curr)

            # publish out the batched message
            self.publish_batched_signals()

        # add to the signal list
        def publish_output_signal(self, output_signal, output_value=0.0, output_passthrough=""):
            output_signal_event_fields = {
                "signal": output_signal,
                "value": float(output_value), # must be numeric
                "passthrough": str(output_passthrough),
            }
            output_msg = AbstractSignal(**output_signal_event_fields)
            self.signal_list.append(output_msg)

        # publish BatchedAbstractSignals
        def publish_batched_signals(self):
            # construct and publish batched message
            msg = BatchedAbstractSignal()
            msg.name = self.msg_namespace
            msg.priority = self.priority
            msg.signals = self.signal_list

            # map to publisher, create a new one if there's no existing map
            if msg.name not in self.publisher_map:
                self.publisher_map[msg.name] = hlib.BatchedAbstractSignalPublisher(namespace=msg.name)
            self.logger.info(f"Published to {self.publisher_map[msg.name].topic}: {msg}")
            self.publisher_map[msg.name].publish(msg)


def main(args=None):
    do_imports(yaml_config)
    abstract_node = AbstractNode()

    while True:
        time.sleep(1.0)

if __name__ == '__main__':
    main()

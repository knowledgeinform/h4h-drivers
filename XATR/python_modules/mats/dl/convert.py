import mats
from tensorflow.keras.models import load_model
import tensorflow as tf
#from pathlib import Path
from tensorflow.keras import backend as K
import os.path as osp
import os
from tensorflow.python.framework import graph_util
from tensorflow.python.framework import graph_io
try:
    import uff
    __TRT = True
except:
    print('TensorRT UFF package is missing.')
    __TRT = False
import h5py


def keras2uff(weight_filename, output_filename, keepPbFile=False):
    out_folder, out_filename = osp.split(output_filename)
    out_basename, out_ext = osp.splitext(out_filename)
    if not out_ext == '.uff':
        mats.mats_log(
            'WARN',
            'Wrong file extension for conversion to UFF. Changed to uff.')
        out_filename = out_basename+'.uff'
    out_uff = out_basename+'.uff'
    out_pb = out_basename+'.pb'

    K.set_learning_phase(0)
    K.set_image_data_format('channels_last')
    try:
        net_model = load_model(weight_filename)
    except:
        print('Modifying model file.')
        fid = h5py.File(weight_filename, 'a')
        del fid.attrs['training_config']
        fid.close()
        net_model = load_model(weight_filename)
    
    if tf.version.VERSION[0] == '2':
        tf.keras.models.save_model(net_model, osp.join(out_folder, out_pb),
                                   overwrite=True, include_optimizer=True,
                                   save_format='tf')
    else:
        # Assuming 1 output
        pred = tf.identity(net_model.outputs[0], name='output_node0')

        sess = K.get_session()
        constant_graph = graph_util.convert_variables_to_constants(
            sess, sess.graph.as_graph_def(), ['output_node0'])
        constant_graph = graph_util.remove_training_nodes(constant_graph)
        graph_io.write_graph(constant_graph, out_folder, out_pb, as_text=False)

    if __TRT:
        if tf.version.VERSION[0] == '2':
            model, inputs, outputs = uff.from_tensorflow(
                graphdef=osp.join(out_folder, out_pb, 'saved_model.pb'),
                # output_nodes=['dense_1/Softmax'],
                output_filename=osp.join(out_folder, out_uff),
                return_graph_info=True
            )
            input_name = inputs[0].name
            output_name = outputs[0].name
        else:
            model, inputs, outputs = uff.from_tensorflow(
                graphdef=osp.join(out_folder, out_pb),
                # output_nodes=['dense_1/Softmax'],
                output_filename=osp.join(out_folder, out_uff),
                return_graph_info=True
            )
    else:
        print('TensorRT UFF package is missing. Unable to create UFF file.')
        input_name = None
        output_name = None

    if not keepPbFile:
        os.remove(osp.join(out_folder, out_pb))

    return (input_name, output_name)


def load_pb(path_to_pb):
    with tf.gfile.GFile(path_to_pb, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
    with tf.Graph().as_default() as graph:
        tf.import_graph_def(graph_def, name='')
        return graph
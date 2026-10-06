import tensorflow.keras as keras
from tensorflow.keras import backend as K
import numpy as np


class Recall(keras.layers.Layer):
    def __init__(self, name = "recall/sensitivity", **kwargs):
        super(Recall, self).__init__(name = name, **kwargs);
        self.stateful = True;
        self.true_positives = K.variable(value = 0, dtype = "int32"); self.false_negatives = K.variable(value = 0, dtype = "int32");

    def reset_states(self):
        K.set_value(self.true_positives, 0); K.set_value(self.false_negatives, 0);

    def __call__(self, y_true_in, y_pred_in):
        y_true = K.cast(y_true_in[:, 1], "int32");
        y_pred = K.cast(K.round(y_pred_in[:, 1]), "int32");
        y_pred_not = K.cast(K.round(y_pred_in[:, 0]), "int32");
        tp = K.sum(y_true * y_pred); fn = K.sum(y_pred_not * y_true);
        current_true_pos = self.true_positives * 1; current_false_neg = self.false_negatives * 1;
        new_tp = current_true_pos + tp; new_fn = current_false_neg + fn;
        recall = new_tp / (new_tp + new_fn);
        self.add_update(K.update_add(self.true_positives, tp), inputs = [y_true_in, y_pred_in]);
        self.add_update(K.update_add(self.false_negatives, fn), inputs = [y_true_in, y_pred_in]);

        return recall;


class Precision(keras.layers.Layer):
    def __init__(self, name = "precision", **kwargs):
        super(Precision, self).__init__(name = name, **kwargs)
        self.stateful = True;
        self.true_positives = K.variable(value = 0, dtype = "int32"); self.false_positives = K.variable(value = 0, dtype = "int32");

    def reset_states(self):
        K.set_value(self.true_positives, 0); K.set_value(self.false_positives, 0);

    def __call__(self, y_true_in, y_pred_in):
        y_true = K.cast(y_true_in[:,1], "int32");
        y_true_not = K.cast(y_true_in[:,0], "int32");
        y_pred = K.cast(K.round(y_pred_in[:,1]), "int32");
        tp = K.sum(y_true * y_pred); fp = K.sum(y_true_not * y_pred);
        current_true_pos = self.true_positives * 1; current_false_pos = self.false_positives * 1;
        new_tp = current_true_pos + tp; new_fp = current_false_pos + fp;
        precision = new_tp / (new_tp + new_fp);
        self.add_update(K.update_add(self.true_positives, tp), inputs = [y_true_in, y_pred_in]);
        self.add_update(K.update_add(self.false_positives, fp), inputs = [y_true_in, y_pred_in]);

        return precision;


class Specificity(keras.layers.Layer):
    def __init__(self, name = "specificity", **kwargs):
        super(Specificity, self).__init__(name = name, **kwargs);
        self.stateful = True;
        self.true_negatives = K.variable(value = 0, dtype = "int32"); self.false_positives = K.variable(value = 0, dtype = "int32");

    def reset_states(self):
        K.set_value(self.true_negatives, 0); K.set_value(self.false_positives, 0);

    def __call__(self, y_true_in, y_pred_in):
        y_true_not = K.cast(y_true_in[:,0], "int32");
        y_pred_not = K.cast(K.round(y_pred_in[:,0]), "int32");
        y_pred = K.cast(K.round(y_pred_in[:,1]), "int32");
        tn = K.sum(y_true_not * y_pred_not); fp = K.sum(y_true_not * y_pred);
        current_true_neg = self.true_negatives * 1; current_false_pos = self.false_positives * 1;
        new_tn = current_true_neg + tn; new_fp = current_false_pos + fp;
        specificity = new_tn / (new_tn + new_fp);
        self.add_update(K.update_add(self.true_negatives, tn), inputs = [y_true_in, y_pred_in]);
        self.add_update(K.update_add(self.false_positives, fp), inputs = [y_true_in, y_pred_in]);

        return specificity;


class WeightedAccuracy(keras.layers.Layer):
    def __init__(self, name = "weighted_acc", **kwargs):
        super(WeightedAccuracy, self).__init__(name = name, **kwargs);
        self.stateful = True;
        self.positives = K.variable(value = 0, dtype = "int32"); self.negatives = K.variable(value = 0, dtype = "int32");
        self.true_positives = K.variable(value = 0, dtype = "int32"); self.true_negatives = K.variable(value = 0, dtype = "int32");
        self.class_weight = {0: 1, 1: 5};

    def reset_states(self):
        K.set_value(self.positives, 0); K.set_value(self.negatives, 0);
        K.set_value(self.true_positives, 0); K.set_value(self.true_negatives, 0);

    def __call__(self, y_true_in, y_pred_in):
        class_weight_arr = np.array([self.class_weight[0], self.class_weight[1]]);
        y_true = K.cast(y_true_in[:, 1], "int32");
        y_pred = K.cast(K.round(y_pred_in[:, 1]), "int32");
        y_true_not = K.cast(y_true_in[:, 0], "int32");
        y_pred_not = K.cast(K.round(y_pred_in[:, 0]), "int32");
        pos = K.sum(y_true); neg = K.sum(y_true_not);
        tn = K.sum(y_true_not * y_pred_not); tp = K.sum(y_true * y_pred);
        current_pos = self.positives * 1; current_neg = self.negatives * 1;
        current_tn = self.true_negatives * 1; current_tp = self.true_positives * 1;
        new_pos = K.cast(current_pos + pos, "float32"); new_neg = K.cast(current_neg + neg, "float32");
        new_tn = K.cast(current_tn + tn, "float32"); new_tp = K.cast(current_tp + tp, "float32");
        num = class_weight_arr[0] * new_tn + class_weight_arr[1] * new_tp;
        denom = class_weight_arr[0] * new_neg + class_weight_arr[1] * new_pos;
        self.add_update(K.update_add(self.positives,pos), inputs=[y_true_in, y_pred_in]);
        self.add_update(K.update_add(self.negatives,neg), inputs=[y_true_in, y_pred_in]);
        self.add_update(K.update_add(self.true_positives,tp), inputs=[y_true_in, y_pred_in]);
        self.add_update(K.update_add(self.true_negatives,tn), inputs=[y_true_in, y_pred_in]);

        return num / denom;


class TruePositives(keras.layers.Layer):
    def __init__(self, name = "tp", **kwargs):
        super(TruePositives, self).__init__(name = name, **kwargs);
        self.stateful = True;
        self.true_positives = K.variable(value = 0, dtype = "int32");

    def reset_states(self):
        K.set_value(self.true_positives, 0);

    def __call__(self, y_true_in, y_pred_in):
        y_true = K.cast(y_true_in[:, 1], "int32");
        y_pred = K.cast(K.round(y_pred_in[:, 1]), "int32");
        tp = K.sum(y_true * y_pred);
        current_true_pos = self.true_positives * 1;
        new_tp = current_true_pos + tp;
        self.add_update(K.update_add(self.true_positives, tp), inputs=[y_true_in, y_pred_in]);

        return new_tp;


class TrueNegatives(keras.layers.Layer):
    def __init__(self, name = "tn", **kwargs):
        super(TrueNegatives, self).__init__(name = name, **kwargs);
        self.stateful = True;
        self.true_negatives = K.variable(value = 0, dtype = "int32");

    def reset_states(self):
        K.set_value(self.true_negatives, 0);

    def __call__(self, y_true_in, y_pred_in):
        y_true_not = K.cast(y_true_in[:, 0], "int32");
        y_pred_not = K.cast(K.round(y_pred_in[:, 0]), "int32");
        tn = K.sum(y_true_not * y_pred_not);
        current_true_neg = self.true_negatives * 1;
        new_tn = current_true_neg + tn;
        self.add_update(K.update_add(self.true_negatives, tn), inputs=[y_true_in, y_pred_in]);

        return new_tn;


class FalsePositives(keras.layers.Layer):
    def __init__(self, name = "fp", **kwargs):
        super(FalsePositives, self).__init__(name = name, **kwargs);
        self.stateful = True;
        self.false_positives = K.variable(value = 0, dtype = "int32");

    def reset_states(self):
        K.set_value(self.false_positives, 0);

    def __call__(self, y_true_in, y_pred_in):
        y_true_not = K.cast(y_true_in[:, 0], "int32");
        y_pred = K.cast(K.round(y_pred_in[:, 1]), "int32");
        fp = K.sum(y_true_not * y_pred);
        current_false_pos = self.false_positives * 1;
        new_fp = current_false_pos + fp;
        self.add_update(K.update_add(self.false_positives, fp), inputs = [y_true_in, y_pred_in]);

        return new_fp;


class FalseNegatives(keras.layers.Layer):
    def __init__(self, name = "fn", **kwargs):
        super(FalseNegatives, self).__init__(name = name, **kwargs);
        self.stateful = True;
        self.false_negatives = K.variable(value = 0, dtype = "int32");

    def reset_states(self):
        K.set_value(self.false_negatives, 0);

    def __call__(self, y_true_in, y_pred_in):
        y_true = K.cast(y_true_in[:, 1], "int32");
        y_pred_not = K.cast(K.round(y_pred_in[:, 0]), "int32");
        fn = K.sum(y_pred_not * y_true);
        current_false_neg = self.false_negatives * 1;
        new_fn = current_false_neg + fn;
        self.add_update(K.update_add(self.false_negatives, fn), inputs=[y_true_in, y_pred_in]);

        return new_fn;

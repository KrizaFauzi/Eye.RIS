from keras.utils import register_keras_serializable
from keras import layers
from keras.utils import get_custom_objects


@register_keras_serializable(package="custom_layers")
class GAM(layers.Layer):
    """
    Placeholder implementation of GAM custom layer used by the saved model.
    This implementation is intentionally minimal: it stores the config and
    returns inputs unchanged. It exists only to allow deserialization of
    the pickled model in environments where the original custom class
    definition is not available.
    If you have the original implementation, replace this with it for
    correct behavior.
    """

    def __init__(self, name="gam", trainable=True, dtype="float32", reduction_ratio=16, **kwargs):
        super().__init__(name=name, trainable=trainable, dtype=dtype, **kwargs)
        self.reduction_ratio = reduction_ratio

    def get_config(self):
        cfg = super().get_config()
        cfg.update({
            "reduction_ratio": self.reduction_ratio,
        })
        return cfg

    def call(self, inputs):
        # Minimal behavior: identity. Replace with real computation if known.
        return inputs


# Ensure the class is available in Keras custom objects under the simple name
# so deserialization that expects 'GAM' can find it.
try:
    get_custom_objects()["GAM"] = GAM
except Exception:
    # best-effort; if keras API differs, ignore silently
    pass

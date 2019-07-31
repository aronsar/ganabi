from utils import parse_args
import importlib
import load_data
import gin


@gin.configurable
class TrainConfig(object):
    def __init__(self, args,
                 optimizer=None,
                 loss=None,
                 metrics=None,
                 batch_size=None,
                 epochs=None):
        self.optimizer = optimizer
        self.loss = loss
        self.metrics = metrics
        self.batch_size = batch_size
        self.epochs = epochs


# def main(data, args):
# trainer = Trainer(args) # gin configured

# #FIXME: combine into one line once stuff works
# mode_module = importlib.import_module(args.mode)
# model = mode_module.build_model(args)

# model.compile(
# optimizer = trainer.optimizer,
# loss = trainer.loss,
# metrics = trainer.metrics)

# tr_history = model.fit_generator(
# generator = data.generator('train'),
# verbose = 2, # one line per epoch
# batch_size = trainer.batch_size,
# epochs = trainer.epochs, # = total data / batch_size
# validation_split = 0.1, # fraction of data used for val
# shuffle = True)

# return model

def train_model(data, args):
    train_config = TrainConfig(args)
    mode_module = importlib.import_module("modes." + args.mode)

    train_generator = mode_module.DataGenerator(data.train_data)
    val_generator = mode_module.DataGenerator(data.validation_data)

    model = mode_module.build_model(args)

    model.compile(
        optimizer=train_config.optimizer,
        loss=train_config.loss,
        metrics=train_config.metrics)

    model.fit_generator(
        generator=train_generator,
        validation_data=val_generator,
        verbose=2,
        epochs=train_config.epochs,
        shuffle=True)

    return model

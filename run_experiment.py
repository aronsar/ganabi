"""
This script is meant as an end to end, data creator, trainer, and evaluater.
It is set up so that the tasks within can easily be done manually as well,
by splitting up the tasts into separate scripts/modules.
"""
import gin
import keras

from utils.parse_args import parse
from train import train_model
from create_load_data import create_load_data
from evaluate import evaluate_model


def main():
    args = parse()

    gin.external_configurable(keras.optimizers.Adam, module='keras.optimizers')
    gin.external_configurable(keras.losses.categorical_crossentropy, module='keras.losses')
    gin.parse_config_file(args.config_path)

    data = create_load_data(args)

    model = train_model(data, args)

    evaluate_model(data, model, args)


if __name__ == "__main__":
    main()

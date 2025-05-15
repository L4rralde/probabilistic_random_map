from argparse import ArgumentParser, BooleanOptionalAction

from special_scenes import PrmStarScene


def parse_args() -> object:
    parser = ArgumentParser()

    parser.add_argument(
        "--width",
        default = 720,
        type = int,
        help = "Ancho en píxeles de la ventana"
    )
    parser.add_argument(
        "--fps",
        default = 20,
        type = int,
        help = "FPS de la simulación"
    )
    parser.add_argument(
        '--patological',
        action = BooleanOptionalAction,
        help = "Utiliza un escenario Patológico"
    )
    parser.add_argument(
        "--n_samples",
        default = 50,
        type = int,
        help = "Número total de muestras en Xfree"
    )

    args = parser.parse_args()
    return args

def main() -> None:
    args = parse_args()

    scene = PrmStarScene(
        title = "PRM",
        width = args.width,
        height = args.width,
        max_fps = args.fps,
        patological = args.patological,
        background_color = 	(1.0, 1.0, 1.0, 1.0),
        n_samples = args.n_samples
    )
    scene.run()


if __name__ == '__main__':
    main()

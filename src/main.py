from argparse import ArgumentParser

from special_scenes import PrmScene

def parse_args() -> object:
    parser = ArgumentParser()

    parser.add_argument(
        "--width",
        default = 720,
        type = int,
        help = "Ancho en píxeles de la ventana"
    )
    parser.add_argument(
        "--height",
        default = 720,
        type = int,
        help = "Altura en píxeles de la ventana"
    )
    parser.add_argument(
        "--fps",
        default = 20,
        type = int,
        help = "FPS de la simulación"
    )

    args = parser.parse_args()
    return args

def main() -> None:
    args = parse_args()

    scene = PrmScene(
        title = "PRM",
        width = args.width,
        height = args.height,
        max_fps = args.fps,
        background_color = 	(1.0, 1.0, 1.0, 1.0)
    )
    scene.run()


if __name__ == '__main__':
    main()

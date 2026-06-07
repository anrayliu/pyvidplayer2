import importlib.util
import numpy as np

CV = 0
if importlib.util.find_spec("cv2") is not None:
    CV = 1
    import cv2


class PostProcessing:
    """Used to apply various filters to video playback. Requires OpenCV."""

    @staticmethod
    def none(data: np.ndarray) -> np.ndarray:
        """Default. Nothing happens."""

        return data

    if CV:
        @staticmethod
        def blur(data: np.ndarray) -> np.ndarray:
            """Slightly blurs frames."""

            return cv2.blur(data, (5, 5))

        @staticmethod
        def greyscale(data: np.ndarray) -> np.ndarray:
            """Removes colour from frame."""

            return np.stack((cv2.cvtColor(data, cv2.COLOR_BGR2GRAY),) * 3, axis=-1)

        @staticmethod
        def noise(data: np.ndarray) -> np.ndarray:
            """Adds a static-like filter. Very resource intensive."""

            noise = np.zeros(data.shape, dtype=np.uint8)
            cv2.randn(noise, (0,) * 3, (20,) * 3)
            return data + noise

        @staticmethod
        def letterbox(data: np.ndarray) -> np.ndarray:
            """Adds black bars above and below the frame to look more cinematic."""

            background = np.zeros((*data.shape[:2], 3), dtype=np.uint8)

            # topleft crop
            x1, y1 = 0, int(data.shape[0] * 0.1)

            # bottomright crop
            x2, y2 = data.shape[1], int(data.shape[0] * 0.9)

            # crops image
            data = data[y1:y2, x1:x2]

            # draws image onto background
            background[y1:y1 + data.shape[0], x1:x1 + data.shape[1]] = data

            return background

        @staticmethod
        def cel_shading(data: np.ndarray) -> np.ndarray:
            """Thickens borders for a comic book style filter."""

            return cv2.subtract(data, cv2.blur(cv2.merge((cv2.Canny(data, 150, 200),) * 3), (2, 2)))

        @staticmethod
        def flipup(data: np.ndarray) -> np.ndarray:
            """Flips the video across x-axis."""

            return np.flipud(data)

        @staticmethod
        def fliplr(data: np.ndarray) -> np.ndarray:
            """Flips the video across y-axis."""

            return np.fliplr(data)

        @staticmethod
        def rotate90(data: np.ndarray) -> np.ndarray:
            """Rotates the video by 90 degrees."""

            return np.rot90(data, k=3)

        @staticmethod
        def rotate270(data: np.ndarray) -> np.ndarray:
            """Essentially just rotate90 but in the other direction."""

            return np.rot90(data, k=1)

        @staticmethod
        def vhs(data: np.ndarray) -> np.ndarray:
            """Old tv effect."""

            shift = 6
            result = data.copy()
            result[:, shift:, 2] = data[:, :-shift, 2]
            result[:, :-shift, 0] = data[:, shift:, 0]

            hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
            hsv[:, :, 1] *= 1.4
            hsv[:, :, 2] *= 0.85
            result = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
            scanlines = np.ones_like(result, dtype=np.float32)
            scanlines[::2] *= 0.75
            return np.clip(result * scanlines, 0, 255).astype(np.uint8)

        @staticmethod
        def emboss(data: np.ndarray) -> np.ndarray:
            """3d paper-like effect."""

            gray = cv2.cvtColor(data, cv2.COLOR_BGR2GRAY)
            kernel = np.array([[-2, -1, 0],
                               [-1, 1, 1],
                               [0, 1, 2]], dtype=np.float32)
            embossed = cv2.filter2D(gray, -1, kernel) + 128
            embossed = np.clip(embossed, 0, 255).astype(np.uint8)
            return cv2.cvtColor(embossed, cv2.COLOR_GRAY2BGR)

        @staticmethod
        def sharpen(data: np.ndarray) -> np.ndarray:
            """Slightly sharpens frames."""

            kernel = np.array([[0, -1, 0],
                               [-1, 5, -1],
                               [0, -1, 0]], dtype=np.float32)
            return np.clip(cv2.filter2D(data, -1, kernel), 0, 255).astype(np.uint8)

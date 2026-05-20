import numpy as np

try:
    import cv2
except ImportError:
    CV = 0
else:
    CV = 1


class PostProcessing:
    def none(data: np.ndarray) -> np.ndarray:
        return data

    if CV:
        def blur(data: np.ndarray) -> np.ndarray:
            return cv2.blur(data, (5, 5))

        def greyscale(data: np.ndarray) -> np.ndarray:
            return np.stack((cv2.cvtColor(data, cv2.COLOR_BGR2GRAY),) * 3, axis=-1)

        def noise(data: np.ndarray) -> np.ndarray:
            noise = np.zeros(data.shape, dtype=np.uint8)
            cv2.randn(noise, (0,) * 3, (20,) * 3)
            return data + noise

        def letterbox(data: np.ndarray) -> np.ndarray:
            background = np.zeros((*data.shape[:2], 3), dtype=np.uint8)

            x1, y1 = 0, int(data.shape[0] * 0.1)  # topleft crop
            x2, y2 = data.shape[1], int(data.shape[0] * 0.9)  # bottomright crop
            data = data[y1:y2, x1:x2]  # crops image
            background[y1:y1 + data.shape[0], x1:x1 + data.shape[1]] = data  # draws image onto background

            return background

        def cel_shading(data: np.ndarray) -> np.ndarray:
            return cv2.subtract(data, cv2.blur(cv2.merge((cv2.Canny(data, 150, 200),) * 3), (2, 2)))

        def flipup(data: np.ndarray) -> np.ndarray:
            return np.flipud(data)

        def fliplr(data: np.ndarray) -> np.ndarray:
            return np.fliplr(data)

        def rotate90(data: np.ndarray) -> np.ndarray:
            return np.rot90(data, k=3)

        def rotate270(data: np.ndarray) -> np.ndarray:
            return np.rot90(data, k=1)

        def vhs(data: np.ndarray) -> np.ndarray:
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

        def emboss(data: np.ndarray) -> np.ndarray:
            gray = cv2.cvtColor(data, cv2.COLOR_BGR2GRAY)
            kernel = np.array([[-2, -1, 0],
                               [-1,  1, 1],
                               [ 0,  1, 2]], dtype=np.float32)
            embossed = cv2.filter2D(gray, -1, kernel) + 128
            embossed = np.clip(embossed, 0, 255).astype(np.uint8)
            return cv2.cvtColor(embossed, cv2.COLOR_GRAY2BGR)

        def sharpen(data: np.ndarray) -> np.ndarray:
            kernel = np.array([[ 0, -1,  0],
                               [-1,  5, -1],
                               [ 0, -1,  0]], dtype=np.float32)
            return np.clip(cv2.filter2D(data, -1, kernel), 0, 255).astype(np.uint8)

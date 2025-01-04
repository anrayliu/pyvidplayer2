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
        
        def sharpen(data: np.ndarray) -> np.ndarray:
            return cv2.filter2D(data, -1, np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]]))
        
        def greyscale(data: np.ndarray) -> np.ndarray:
            return np.stack((cv2.cvtColor(data, cv2.COLOR_BGR2GRAY),) * 3, axis=-1)
        
        def noise(data: np.ndarray) -> np.ndarray:
            noise = np.zeros(data.shape, dtype=np.uint8)
            cv2.randn(noise, (0,) * 3, (20,) * 3)
            return data + noise
        
        def letterbox(data: np.ndarray) -> np.ndarray:
            background = np.zeros((*data.shape[:2], 3), dtype=np.uint8)

            x1, y1 = 0, int(data.shape[0] * 0.1)                            # topleft crop
            x2, y2 = data.shape[1], int(data.shape[0] * 0.9)                # bottomright crop
            data = data[y1:y2, x1:x2]                                       # crops image
            background[y1:y1 + data.shape[0], x1:x1 + data.shape[1]] = data # draws image onto background

            return background
        
        def cel_shading(data: np.ndarray) -> np.ndarray:
            return cv2.subtract(data, cv2.blur(cv2.merge((cv2.Canny(data, 150, 200),) * 3), (2, 2)))

        def flipup(data: np.ndarray) -> np.ndarray:
            return np.flipud(data)

        def fliplr(data: np.ndarray) -> np.ndarray:
            return np.fliplr(data)

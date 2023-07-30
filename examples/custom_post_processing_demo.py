'''
This example shows how you can merge and create new post processing functions
'''


from pyvidplayer2 import Video, PostProcessing

# applies a letterbox, cel shading, and greyscale to video

def custom_process(data):
    return PostProcessing.letterbox(PostProcessing.cel_shading(PostProcessing.greyscale(data)))

Video(r"resources\birds.avi", post_process=custom_process).preview()
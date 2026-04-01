# netTune

Online music streaming server using raw sockets. can stream to multiple clients.

## Working

Server streams music in fixed number of bytes. The client recieves these packets in a thread safe queue, adds them to a buffer from which the hardware fetches and plays at required rate(specific to each client).

## Why a queue and a buffer

Essentially only 1 buffer is required. But in this implementation of client, we used a thread safe queue(to avoid collisions during read and writes at the same time). In this queue, each element is of particular size, different from the amounts required by the client hardware need at every instant. Hence we have a byte array that continously collects bytes from the queue until required amount is reached.

### How is music played on client side?

Client internally uses pyaudio to play the music, but the required number of bytes to play the audio need to be given by the client itself.

Some basics terms:

Music basically contains samples(a unit/piece of a wave)

![alt text](assets/image.png)

Frames are sets of samples (when audio is mono 1 frame = 1 sample, when audio is stereo (left and right speakers have seprate waves) then each frame contains 2 samples).

framerate is the number of frames that need to be played per second, where as frame_count is the number of frames requested by the hardware at a given instant

Suppose the frame_rate=44100 and frame count is 512 then the callback is called 44100/512= 86 times every second.

The client first gets details about the music file like samplewidth, channels, framerate and opens a pyaudio object. This object inturn creates a seprate thread internally that runs the callback when the hardware needs it.

The networks thread continously fills the queue with data.
The callback runs the read_buf function to read data from queue to buffer. The number of bits read= the framecount* number of bytes per sample* no of channels.

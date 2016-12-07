import numpy
import os
import tempfile
import wave

from amen.exceptions import AmenError

from ffmpeg import ffmpeg

class AudioRenderable(object):
    """
    An object that gives an `AudioData` in response to a call to its `render`\()
    method.
    Intended to be an abstract class that helps enforce the `AudioRenderable`
    protocol. Picked up a couple of convenience methods common to many descendants.

    Every `AudioRenderable` must provide three things:

    render()
        A method returning the `AudioData` for the object. The rhythmic duration (point
        at which any following audio is appended) is signified by the `endindex` accessor,
        measured in samples.
    source
        An accessor pointing to the `AudioData` that contains the original sample data of
        (a superset of) this audio object.
    duration
        An accessor returning the rhythmic duration (in seconds) of the audio object.
    """
    def resolve_source(self, alt):
        """
        Given an alternative, fallback `alt` source, return either `self`'s
        source or the alternative. Throw an informative error if no source
        is found.

        Utility code that ended up being replicated in several places, so
        it ended up here. Not necessary for use in the RenderableAudioObject
        protocol.
        """
        if hasattr(self, 'source'):
            source = self.source
        else:
            if isinstance(alt, AudioData):
                source = alt
            else:
                raise AmenError("%s has no implicit or explicit source \
                                                during rendering." %
                                                (self.__class__.__name__, ))
        return source

    @staticmethod
    def init_audio_data(source, num_samples):
        """
        Convenience function for rendering: return a pre-allocated, zeroed
        `AudioData`.
        """
        if source.numChannels > 1:
            newchans = source.numChannels
            newshape = (num_samples, newchans)
        else:
            newchans = 1
            newshape = (num_samples,)
        return AudioData32(shape=newshape, sampleRate=source.sampleRate,
                            numChannels=newchans, defer=False)

    def sources(self):
        return set([self.source])

    def encode(self, filename):
        """
        Shortcut function that takes care of the need to obtain an `AudioData`
        object first, through `render`.
        """
        self.render().encode(filename)

class AudioData(AudioRenderable):
    """
    Handles audio data transparently. A smart audio container
    with accessors that include:

    sampleRate
        samples per second
    numChannels
        number of channels
    data
        a `numpy.array`_

    .. _numpy.array: http://docs.scipy.org/doc/numpy/reference/generated/numpy.array.html
    """
    def __init__(self, filename=None, ndarray=None, shape=None, sampleRate=None, numChannels=None, defer=False, verbose=True):
        """
        Given an input `ndarray`, import the sample values and shape
        (if none is specified) of the input `numpy.array`.

        Given a `filename` (and an input ndarray), use ffmpeg to convert
        the file to wave, then load the file into the data,
        auto-detecting the sample rate, and number of channels.

        :param filename: a path to an audio file for loading its sample
            data into the AudioData.data
        :param ndarray: a `numpy.array`_ instance with sample data
        :param shape: a tuple of array dimensions
        :param sampleRate: sample rate, in Hz
        :param numChannels: number of channels

        .. _numpy.array: http://docs.scipy.org/doc/numpy/reference/generated/numpy.array.html
        """
        self.verbose = verbose
        self.defer = defer
        self.filename = filename
        self.sampleRate = sampleRate
        self.numChannels = numChannels
        self.convertedfile = None
        self.endindex = 0
        if shape is None and isinstance(ndarray, numpy.ndarray) and not self.defer:
            self.data = numpy.zeros(ndarray.shape, dtype=numpy.int16)
        elif shape is not None and not self.defer:
            self.data = numpy.zeros(shape, dtype=numpy.int16)
        elif not self.defer and self.filename:
            self.data = None
            self.load()
        else:
            self.data = None
        if ndarray is not None and self.data is not None:
            self.endindex = len(ndarray)
            self.data[0:self.endindex] = ndarray

    def load(self):
        if isinstance(self.data, numpy.ndarray):
            return
        temp_file_handle = None
        if self.filename.lower().endswith(".wav") and (self.sampleRate, self.numChannels) == (44100, 2):
            file_to_read = self.filename
        elif self.convertedfile:
            file_to_read = self.convertedfile
        else:
            temp_file_handle, self.convertedfile = tempfile.mkstemp(".wav")
            self.sampleRate, self.numChannels = ffmpeg(self.filename, self.convertedfile, overwrite=True,
                    numChannels=self.numChannels, sampleRate=self.sampleRate, verbose=self.verbose)
            file_to_read = self.convertedfile

        w = wave.open(file_to_read, 'r')
        numFrames = w.getnframes()
        raw = w.readframes(numFrames)
        sampleSize = numFrames * self.numChannels
        data = numpy.frombuffer(raw, dtype="<h", count=sampleSize)
        ndarray = numpy.array(data, dtype=numpy.int16)
        if self.numChannels > 1:
            ndarray.resize((numFrames, self.numChannels))
        self.data = numpy.zeros(ndarray.shape, dtype=numpy.int16)
        self.endindex = 0
        if ndarray is not None:
            self.endindex = len(ndarray)
            self.data = ndarray
        if temp_file_handle is not None:
            os.close(temp_file_handle)
        w.close()

    def __getitem__(self, index):
        """
        Fetches a frame or slice. Returns an individual frame (if the index
        is a time offset float or an integer sample number) or a slice if
        the index is an `AudioQuantum` (or quacks like one).
        """
        if not isinstance(self.data, numpy.ndarray) and self.defer:
            self.load()
        if isinstance(index, float):
            index = int(index * self.sampleRate)
        elif hasattr(index, "start") and hasattr(index, "duration"):
            index =  slice(float(index.start), index.start + index.duration)

        if isinstance(index, slice):
            if (hasattr(index.start, "start") and
                 hasattr(index.stop, "duration") and
                 hasattr(index.stop, "start")):
                index = slice(index.start.start, index.stop.start + index.stop.duration)

        if isinstance(index, slice):
            return self.getslice(index)
        else:
            return self.getsample(index)

    def getslice(self, index):
        "Help `__getitem__` return a new AudioData for a given slice"
        if not isinstance(self.data, numpy.ndarray) and self.defer:
            self.load()
        if isinstance(index.start, float):
            index = slice(int(index.start * self.sampleRate),
                            int(index.stop * self.sampleRate), index.step)
        return AudioData(None, self.data[index], sampleRate=self.sampleRate,
                            numChannels=self.numChannels, defer=False)

    def getsample(self, index):
        """
        Help `__getitem__` return a frame (all channels for a given
        sample index)
        """
        if not isinstance(self.data, numpy.ndarray) and self.defer:
            self.load()
        if isinstance(index, int):
            return self.data[index]
        else:
            #let the numpy array interface be clever
            return AudioData(None, self.data[index], defer=False)

    def pad_with_zeros(self, num_samples):
        if num_samples > 0:
            if self.numChannels == 1:
                extra_shape = (num_samples,)
            else:
                extra_shape = (num_samples, self.numChannels)
            self.data = numpy.append(self.data,
                                     numpy.zeros(extra_shape, dtype=numpy.int16), axis=0)

    def append(self, another_audio_data):
        "Appends the input to the end of this `AudioData`."
        extra = len(another_audio_data.data) - (len(self.data) - self.endindex)
        self.pad_with_zeros(extra)
        self.data[self.endindex : self.endindex + len(another_audio_data)] += another_audio_data.data
        self.endindex += another_audio_data.endindex

    def sum(self, another_audio_data):
        extra = len(another_audio_data.data) - len(self.data)
        self.pad_with_zeros(extra)
        compare_limit = min(len(another_audio_data.data), len(self.data)) - 1
        self.data[: compare_limit] += another_audio_data.data[: compare_limit]

    def add_at(self, time, another_audio_data):
        """
        Adds the input `another_audio_data` to this `AudioData` 
        at the `time` specified in seconds. If `another_audio_data` has fewer channels than
        this `AudioData`, the `another_audio_data` will be resampled to match.
        In this case, this method will modify `another_audio_data`.

        """
        offset = int(time * self.sampleRate)
        extra = offset + len(another_audio_data.data) - len(self.data)
        self.pad_with_zeros(extra)
        if another_audio_data.numChannels < self.numChannels:
            # Resample another_audio_data
            another_audio_data.data = numpy.repeat(another_audio_data.data, self.numChannels).reshape(len(another_audio_data), self.numChannels)
            another_audio_data.numChannels = self.numChannels
        self.data[offset : offset + len(another_audio_data.data)] += another_audio_data.data 

    def __len__(self):
        if self.data is not None:
            return len(self.data)
        else:
            return 0

    def __add__(self, other):
        """Supports stuff like this: sound3 = sound1 + sound2"""
        return assemble([self, other], numChannels=self.numChannels,
                            sampleRate=self.sampleRate)

    def encode(self, filename=None, mp3=None):
        """
        Outputs an MP3 or WAVE file to `filename`.
        Format is determined by `mp3` parameter.
        """
        if not mp3 and filename.lower().endswith('.wav'):
            mp3 = False
        else:
            mp3 = True
        if mp3:
            foo, tempfilename = tempfile.mkstemp(".wav")
            os.close(foo)
        else:
            tempfilename = filename
        fid = open(tempfilename, 'wb')
        # Based on Scipy svn
        # http://projects.scipy.org/pipermail/scipy-svn/2007-August/001189.html
        fid.write('RIFF')
        fid.write(struct.pack('<i', 0))  # write a 0 for length now, we'll go back and add it later
        fid.write('WAVE')
        # fmt chunk
        fid.write('fmt ')
        if self.data.ndim == 1:
            noc = 1
        else:
            noc = self.data.shape[1]
        bits = self.data.dtype.itemsize * 8
        sbytes = self.sampleRate * (bits / 8) * noc
        ba = noc * (bits / 8)
        fid.write(struct.pack('<ihHiiHH', 16, 1, noc, self.sampleRate, sbytes, ba, bits))
        # data chunk
        fid.write('data')
        fid.write(struct.pack('<i', self.data.nbytes))
        self.data.tofile(fid)
        # Determine file size and place it in correct
        # position at start of the file.
        size = fid.tell()
        fid.seek(4)
        fid.write(struct.pack('<i', size - 8))
        fid.close()
        if not mp3:
            return tempfilename
        # now convert it to mp3
        if not filename.lower().endswith('.mp3'):
            filename = filename + '.mp3'
        try:
            bitRate = MP3_BITRATE
        except NameError:
            bitRate = 128

        try:
            ffmpeg(tempfilename, filename, bitRate=bitRate, verbose=self.verbose)
        except:
            log.warning("Error converting from %s to %s", tempfilename, filename)

        if tempfilename != filename:
            if self.verbose:
                log.warning(sys.stderr, "Deleting: %s", tempfilename)
            os.remove(tempfilename)
        return filename

    def unload(self):
        self.data = None
        if self.convertedfile:
            if self.verbose:
                log.warning("Deleting: %s", self.convertedfile)
            os.remove(self.convertedfile)
            self.convertedfile = None

    def render(self, start=0.0, to_audio=None, with_source=None):
        if not to_audio:
            return self
        if with_source != self:
            return
        to_audio.add_at(start, self)
        return

    @property
    def duration(self):
        return float(self.endindex) / self.sampleRate

    @property
    def source(self):
        return self
#!/usr/bin/python -i
import cPickle, hashlib, sys
import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
import fore.action as action

from echonest.remix.audio import AudioData, AudioAnalysis
class LocalAudioFile(AudioData):
    """
    Cut down from echonest.remix.audio.LocalAudioFile
    Allows provision of analysis pickle as per fore.mixer.LocalAudioStream
    """

    def __init__(self, filename, analysis=None):
        AudioData.__init__(self, filename=filename, verbose=True, defer=False, sampleRate=None, numChannels=None)
        try: tempanalysis = cPickle.loads(analysis)
        except Exception:
            track_md5 = hashlib.md5(file(self.filename, 'rb').read()).hexdigest()

            print >> sys.stderr, "Computed MD5 of file is " + track_md5
            try:
                print >> sys.stderr, "Probing for existing analysis"
                tempanalysis = AudioAnalysis(track_md5)
            except Exception:
                print >> sys.stderr, "Analysis not found. Uploading..."
                tempanalysis = AudioAnalysis(filename)

        self.analysis = tempanalysis
        self.analysis.source = self
        self.is_local = False

from fore.mixer import LocalAudioStream as las
print("You can load MP3 files with LocalAudioFile() or las()")
print("and manipulate them using the functions in action")
print("To save a modified file: save(f, fn)")
def save(f, fn):
    action.audition_render([f.data], fn)
    


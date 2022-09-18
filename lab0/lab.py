# No Imports Allowed!


def backwards(sound):
    out = {"rate": sound["rate"]}
    samples = []
    for i in range(len(sound["samples"]) - 1, -1, -1):
        samples.append(sound["samples"][i])
    out["samples"] = samples
    return out

def mix(sound1, sound2, p):
    if sound1["rate"] != sound2["rate"]:
        return None
    out = {"rate": sound1["rate"]}
    samples = []
    lens = min(len(sound1["samples"]), len(sound2["samples"]))
    for i in range(lens):
        samples.append(sound1["samples"][i]*p + sound2["samples"][i]*(1-p))
    out["samples"] = samples
    return out


# don't know the meaning of this function
def echo(sound, num_echoes, delay, scale):
    sample_delay = round(delay * sound["rate"])
    samples_list = sound["samples"]
    list_of_offsets = []
    length = sample_delay * num_echoes
    added_list = []

    # append added list with zeros corresponding to the length of our desired echo samples list
    for k in range(length + len(samples_list)):
        added_list.append(0)
    new_samples_list = samples_list[::]  # slice list into new list so we don't edit the input

    # iterate through each echo
    for i in range(num_echoes):
        offset_list = []  # initialize empty offet list for each echo
        for j in range(sample_delay * (i + 1)):  # add zeros to begging of list to represent the echo offset
            offset_list.append(0)
        for sample in samples_list:  # add scaled samples to offset list
            offset_list.append(sample * (scale ** (i + 1)))
        for i in range(length - (sample_delay * (i + 1))):  # append zeros to end of offset list to ensure offset list
            offset_list.append(0)  # is as long oas the desired echo samples list length
        list_of_offsets.append(offset_list)  # append list of echo lists with current echo offset list

    # add zeros to end of samples list to ensure sampled list is the length of desired echo list
    for i in range(sample_delay * num_echoes):
        new_samples_list.append(0)

    # add all of the offset lists and the original list together to get desired echo list
    for lst in list_of_offsets:
        for i in range(len(lst)):
            added_list[i] += lst[i]
    for i in range(len(samples_list)):
        added_list[i] += new_samples_list[i]

    return {"rate": sound["rate"], "samples": added_list}  # return dict with echo list

def pan(sound):
    out_left = []
    out_right = []
    length = len(sound["left"])

    for i in range(length):
        print(i, length)
        out_left.append(sound["left"][i] * (1.0 - i/(length - 1)))
        out_right.append(sound["right"][i] * (i/(length - 1)))
    return {"rate":sound["rate"], "left":out_left, "right":out_right}

def remove_vocals(sound):
    out = []
    for i in range(len(sound["left"])):
       out.append(sound["left"][i] - sound["right"][i])
    return {"rate": sound["rate"], "samples": out}

# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds

import io
import wave
import struct


def load_wav(filename, stereo=False):
    """
    Given the filename of a WAV file, load the data from that file and return a
    Python dictionary representing that sound
    """
    f = wave.open(filename, "r")
    chan, bd, sr, count, _, _ = f.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {"rate": sr}

    if stereo:
        left = []
        right = []
        for i in range(count):
            frame = f.readframes(1)
            if chan == 2:
                left.append(struct.unpack("<h", frame[:2])[0])
                right.append(struct.unpack("<h", frame[2:])[0])
            else:
                datum = struct.unpack("<h", frame)[0]
                left.append(datum)
                right.append(datum)

        out["left"] = [i / (2**15) for i in left]
        out["right"] = [i / (2**15) for i in right]
    else:
        samples = []
        for i in range(count):
            frame = f.readframes(1)
            if chan == 2:
                left = struct.unpack("<h", frame[:2])[0]
                right = struct.unpack("<h", frame[2:])[0]
                samples.append((left + right) / 2)
            else:
                datum = struct.unpack("<h", frame)[0]
                samples.append(datum)

        out["samples"] = [i / (2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Given a dictionary representing a sound, and a filename, convert the given
    sound into WAV format and save it as a file with the given filename (which
    can then be opened by most audio players)
    """
    outfile = wave.open(filename, "w")

    if "samples" in sound:
        # mono file
        outfile.setparams((1, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = [int(max(-1, min(1, v)) * (2**15 - 1)) for v in sound["samples"]]
    else:
        # stereo
        outfile.setparams((2, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = []
        for l, r in zip(sound["left"], sound["right"]):
            l = int(max(-1, min(1, l)) * (2**15 - 1))
            r = int(max(-1, min(1, r)) * (2**15 - 1))
            out.append(l)
            out.append(r)

    outfile.writeframes(b"".join(struct.pack("<h", frame) for frame in out))
    outfile.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/meow.wav, rather than just as meow.wav, to account for the sound
    # files being in a different directory than this file)
    meow = load_wav("sounds/meow.wav")

    # write_wav(backwards(meow), 'meow_reversed.wav')

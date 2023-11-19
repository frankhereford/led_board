from recorder import *
from time import perf_counter

bpm_list = []
prev_beat = perf_counter()
low_freq_avg_list = []


def plot_audio_and_detect_beats():
    if not input_recorder.has_new_audio: 
        return

    # get x and y values from FFT
    xs, ys = input_recorder.fft()
    
    # calculate average for all frequency ranges
    y_avg = numpy.mean(ys)

    # calculate low frequency average
    low_freq = [ys[i] for i in range(len(xs)) if xs[i] < 1000]
    low_freq_avg = numpy.mean(low_freq)

    global low_freq_avg_list
    low_freq_avg_list.append(low_freq_avg)
    cumulative_avg = numpy.mean(low_freq_avg_list)
    
    bass = low_freq[:int(len(low_freq)/2)]
    bass_avg = numpy.mean(bass)

    # check if there is a beat
    # song is pretty uniform across all frequencies
    if (y_avg > 10 and (bass_avg > cumulative_avg * 1.5 or
            (low_freq_avg < y_avg * 1.2 and bass_avg > cumulative_avg))):
        global prev_beat
        curr_time = perf_counter()
        # print(curr_time - prev_beat)
        if curr_time - prev_beat > 60/180: # 180 BPM max
            # print("beat")
            
            global bpm_list
            bpm = int(60 / (curr_time - prev_beat))
            if len(bpm_list) < 4:
                if bpm > 60:
                    bpm_list.append(bpm)
            else:
                bpm_avg = int(numpy.mean(bpm_list))
                if abs(bpm_avg - bpm) < 35:
                    bpm_list.append(bpm)
            # reset the timer
            prev_beat = curr_time

    # shorten the cumulative list to account for changes in dynamics
    if len(low_freq_avg_list) > 50:
        low_freq_avg_list = low_freq_avg_list[25:]
        # print("REFRESH!!")

    # keep two 8-counts of BPMs so we can maybe catch tempo changes
    if len(bpm_list) > 24:
        bpm_list = bpm_list[8:]

    # reset song data if the song has stopped
    if y_avg < 10:
        bpm_list = []
        low_freq_avg_list = []
        #uiplot.btnD.setText(_fromUtf8("BPM"))
        # print("new song")



input_recorder = InputRecorder()
input_recorder.start()

print("hi")
while True:
    if len(bpm_list) > 0:
        print(bpm_list)
    plot_audio_and_detect_beats()
print("yo")
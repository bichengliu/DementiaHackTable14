// Example: Record a sound and then play it back.
// We need p5.AudioIn (mic / sound source), p5.SoundRecorder
// (records the sound), and a p5.SoundFile (play back).

var mic, recorder, soundFile;




function setup() {
    // create an audio in
    mic = new p5.AudioIn();


    // users must manually enable their browser microphone for recording to work properly!
    mic.start();

    // create a sound recorder
    recorder = new p5.SoundRecorder();

    // connect the mic to the recorder
    recorder.setInput(mic);

    // create an empty sound file that we will use to playback the recording
    soundFile = new p5.SoundFile();
    recorder.stop();
}


function stop() {
    console.log("stop");
    recorder.stop();
    mic.stop;
    saveSound(soundFile, filename);
    $.ajax({
        url: 'https://memorylog.mybluemix.net/api/analyzedata',
        data: JSON.stringify({
            'filename': 'https://dl.dropboxusercontent.com/u/11606397/' + filename,
            'patient_id': "03",
            'date': "20170304"
        }),
        type: 'POST',
        contentType: 'application/json;charset=UTF-8',
        processData: false,
        success: function (response) {
            console.log(response);
        },
        error: function (error) {
            console.log(error);
        }
    });
}

function tmrStp() {
    console.log('timer');
    stop();
}

function start() {
    console.log("start");

    if (mic.enabled) {
        recorder.record(soundFile);
        setTimeout(tmrStp, 60000);
    } else {
        alert("Please Enable Mic");
    }
}

//setTimeout(tmrStp, 1000);

//
//function mousePressed() {
//    // use the '.enabled' boolean to make sure user enabled the mic (otherwise we'd record silence)
//    if (state === 0 && mic.enabled) {
//
//        // Tell recorder to record to a p5.SoundFile which we will use for playback
//        recorder.record(soundFile);
//
//        background(255, 0, 0);
//        text('Recording now! Click to stop.', 20, 20);
//        state++;
//    } else if (state === 1) {
//        recorder.stop(); // stop recorder, and send the result to soundFile
//
//        background(0, 255, 0);
//        text('Recording stopped. Click to play', 20, 20);
//        state++;
//    } else if (state === 2) {
//        soundFile.play(); // play the result!
//        saveSound(soundFile, 'mySound.wav'); // save file  
//    }
//}

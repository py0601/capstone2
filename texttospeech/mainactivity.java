package com.example.texttospeech_java;


import androidx.appcompat.app.AppCompatActivity;

import android.speech.tts.TextToSpeech;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import java.util.Locale;

import android.os.Bundle;

public class MainActivity extends AppCompatActivity {

    //views
    EditText mTextEt;
    Button mSpeakBtn, mStopBtn;

    TextToSpeech mTTS;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        mTextEt = findViewById(R.id.textEt);
        mSpeakBtn = findViewById(R.id.speakBtn);
        mStopBtn = findViewById(R.id.stopBtn);

        mTTS = new TextToSpeech(getApplicationContext(), new TextToSpeech.OnInitListener() {
            @Override
            public void onInit(int status) {
                if (status != TextToSpeech.ERROR){
                    //if there is no error then set language
                    mTTS.setLanguage(Locale.UK);
                }
                else {
                    Toast.makeText(MainActivity.this, "Error", Toast.LENGTH_SHORT).show();
                }
            }
        });

        //speak btn click
        mSpeakBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                //get text from edit text
                String toSpeak = mTextEt.getText().toString().trim();
                if (toSpeak.equals("")){
                    //if there is no text in edit text
                    Toast.makeText(MainActivity.this, "Please enter text...", Toast.LENGTH_SHORT).show();
                }
                else {
                    Toast.makeText(MainActivity.this, toSpeak, Toast.LENGTH_SHORT).show();
                    //speak the text
                    mTTS.speak(toSpeak, TextToSpeech.QUEUE_FLUSH, null);
                }
            }
        });

        //stop btn click
        mStopBtn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (mTTS.isSpeaking()){
                    //if it is speaking then stop
                    mTTS.stop();
                    //mTTS.shutdown();
                }
                else {
                    //not speaking
                    Toast.makeText(MainActivity.this, "Not speaking", Toast.LENGTH_SHORT).show();
                }
            }
        });
    }

    @Override
    protected void onPause() {
        if (mTTS != null || mTTS.isSpeaking()){
            //if it is speaking then stop
            mTTS.stop();
            //mTTS.shutdown();
        }
        super.onPause();
    }
    }

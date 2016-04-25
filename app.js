var Speaker = require('speaker');
var Generator = require('audio-generator');
var SerialPort = require('serialport').SerialPort;
var uart = new SerialPort('/dev/ttyAMA0',{baudrate:115200});
var noteNum = 0;
var notePer = 80;
var noteScale = 0;
var noteArray = ["C","CS","D","DS","E","F","FS","G","GS","A","AS","B"];
var sub = -1;
var err = 0;
var iErr = 0;
var dErr = 0;
var pNote = 3;
var iNote = 0.01;
var dNote = 0.00;
var noteOutput = 0;
var noteTarget = 0;
var notes = [];
for(var i=0;i<100;i++){
  var note = 16.35*Math.pow(1.05946309,i);
  notes.push(note);
  if(i%12==0){
    sub++;  
  }
  console.log(i+":"+noteArray[i%12]+sub+":"+note);
}
Generator(
	//Generator function, returns sample values -1..1 for channels 
	function (time) {
		if(noteNum==0){
			//return [0,0];
		}
		return [
			30*Math.sin(Math.PI * 2 * time * (noteOutput))*noteScale, //channel 1 
			30*Math.sin(Math.PI * 2 * time * (noteOutput))*noteScale //channel 2 
		];
}).pipe(Speaker({
	channels: 2,
	sampleRate: 44100,
	byteOrder: 'LE',
	bitDepth: 16,
	signed: true,
	float: true,
	interleaved: true,
	mode: 0
}));
var buffer = "";
uart.on('open',function(){
	uart.on('data',function(buf){
		var s = buf.toString();
		for(var i=0;i<buf.length;i++){
			if(s.charAt(i)=='\n'){
				parseBuffer(buffer);
				buffer = "";
			}else{
				buffer+=s.charAt(i);
			}
		}
	});
});
function parseBuffer(buffer){
	var list = buffer.split(" ");
	var prevNote = noteNum;
	noteNum = 0;
	for(var i=0;i<list.length;i++){
		if(list[i]<60){
			noteNum = i+1;
		        noteTarget = notes[48+i];
			noteScale -= (noteScale-((90-list[i])/100+0.1))*0.4;
			break;
		}
	}
    noteOutput += (pNote*err-iNote*iErr-dNote*dErr)/8;
    dErr = iErr;
    iErr = err;
    err = noteTarget - noteOutput;
	if(noteNum==0){
		noteScale -= noteScale*0.05;
		noteNum = prevNote;
	}
}


//board LED is Pin 13
var ledPin = 13;

//web
var url = require('url');
var http = require('http');

//UART
var serialport = require('serialport');
SerialPort = serialport.SerialPort;

//AP700 IP
var ap700_ip=[];
var net = require('net');

//open UART
var myPort = new SerialPort("/dev/ttyS0", {
   baudRate: 57600,
   // look for return and newline at the end of each data packet:
   parser: serialport.parsers.readline("\n")
 });

//define Sensor Temp
var SensorTemp=0;

//Uart Event
myPort.on('open', showPortOpen);
myPort.on('data', sendSerialData);
myPort.on('close', showPortClose);
myPort.on('error', showError);

//Command Type
var cmdtype_led=0;
var cmdtype_pwm=1;
var cmdtype_temp=2;

//Event Function When UART Port Open
function showPortOpen() {
   console.log('port open. Data rate: ' + myPort.options.baudRate);
}

//Event Function When get data from MCU
function sendSerialData(data) {
   console.log(data);
   var obj = JSON.parse(data);
   if (obj.cmd==cmdtype_temp)
   {
       SensorTemp=obj.value;
   }
}

//Event Function When UART  Port Close
function showPortClose() {
   console.log('port closed.');
}

 //Event Function When UART  Error
function showError(error) {
   console.log('Serial port error: ' + error);
 //  SerialPort.close();

}

//http server
var server=http.createServer(function(request, response) {
    //non response favicon
    if (request.url === '/favicon.ico') {
        response.writeHead(200, {'Content-Type': 'image/x-icon'} );
        response.end();
        return;
    }
    try
    {
    //console.log(request.url) ;
     var params = url.parse(request.url, true).query;

     var type=0;


        //led params
        if ( typeof params.value !== 'undefined')
        {
          //LED ON
          if (params.value.toLowerCase() == '1') {
            cmd_led(1);
            //LED OFF
          } else if (params.value.toLowerCase() == '0'){
            cmd_led(0);
          }
       }
       //intensity pwm params && color pwm params
       if (typeof params.intensity !== 'undefined' && typeof params.color !== 'undefined'&& typeof params.type!=='undefined')
       {
         type=1;
          //params.type==0 both
          //params.type==1 A360/160
          //params.type==2 AP700
         if (params.type==0)
         {
             cmd_pwm(params.intensity,params.color);
             cmd_ap700(params.intensity,params.color);
         }
         else if (params.type==1)
         {
              cmd_pwm(params.intensity,params.color);
         }
         else
         {
              cmd_ap700(params.intensity,params.color);
         }
         //cmd_pwm(params.intensity,params.color);
       }
       if(typeof params.temp != 'undefined')
       {
          type=2;
         // cmd_temp(params.temp);
       }
    } catch(e) {
     console.dir(e);
    }

    //response.writeHead(200);
    response.writeHead(200, {"Content-Type":"text/plain"});
    if(type==0)
    {
        response.write("The value written was: " + params.value);
    }
    else if (type==1)
    {
        response.write("The value written was: " + params.intensity+" "+params.color );
    }
    else if (type==2)
    {
        response.write("Temp: " +SensorTemp);
    }
    else
    {
        response.write("The value written was: " + params.value);
    }
    //response.write("The value written was: " + params.value);
    response.end();
}).listen(8081);

server.on('end', function() {
  console.log('there will be no more data.');
});

console.log("http server on 8081 prt");





//cmd function for sent Command to AP700
function cmd_ap700(intensity ,color)
{
  //execute system command to get DHCP List
  var exec = require('child_process').exec;
  var cmd = 'cat /tmp/dhcp.leases';

  exec(cmd, function(error, stdout, stderr) {
       //clear now ap700 IP List
       ap700_ip=[];
       //find ap700 ip list
       findap700(stdout);
       //print ip list array
       console.dir(ap700_ip);
       //gen command
       var buf=new Buffer(2);
       buf[0]=intensity;
       buf[1]=color;
       var data=[0x01, 0x00 , 0x10 ,buf[0],buf[1]];
       if (intensity==0)
       {
         data=[01, 00, 01,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,00,00,00,00,00,0]
       }
       //sent command
       for(var i=0;i<ap700_ip.length;i++)
       {
        data=getSentByte(data);
        sendAP700Cmd(data,ap700_ip[i]);
        //sendAP700Cmd('test',ap700_ip[i]);
       }
  });
}

//Fucntion for sent command to AP700
function sendAP700Cmd(data,ip)
{
try
  {
    //create a socket
    var client = new net.Socket();
    //set Socket timeout
    client.setTimeout(300,function timeout(){
    console.log("timeout"+ip);
    client.end();
    client.destroy();
    });
     //if socket connect success
    client.connect(8899, ip, function() {
    	console.log('Connected'+ip);
      //write command to AP700
    	client.write(new Buffer(data,'hex'));
            client.end();
            client.destroy();
    });
    //when data stream is close
    client.on('end', function(){
      console.log('disconnected from server');
    });
    //when socket have error
    client.on('error', function(){
      console.log('connected to server error');
       client.end();
       client.destroy();
    });

  }
  catch(e)
  {
  }
}

//string to buffer
function str2ab(str) {
  var buf = new ArrayBuffer(str.length*2); // 2 bytes for each char
  var bufView = new Uint16Array(buf);
  for (var i=0, strLen=str.length; i<strLen; i++) {
    bufView[i] = str.charCodeAt(i);
  }
  return buf;
}

//find ap700  form sdu out
function findap700(sduout)
{
   var arr=sduout.split("\n");

   for(var i=0;i<arr.length;i++) {
       try {
         var temp=arr[i].split(" ");
        // console.dir(temp);
        if (temp.length==5)
        {
        // if (temp[3]=="HF-A11")
          if(temp[1]!='undefined' && temp[1].indexOf("ac:cf:23")>-1)
          {
            ap700_ip.push(temp[2]);
          }
        }
       } catch (e) {

       }

    }
}

//gen a LED json command to sent mcu
function cmd_led(turn)
{
   var json="{\"cmd\":"+cmdtype_led+",\"value\":"+turn+"}\n";
   //myPort.write("{\"cmd\":"+cmdtype_led+",\"value\":"+turn+"}\n");
   myPort.write(json);
   console.log(json);
}

//gen a PWM json command to sent mcu
function cmd_pwm(intesity,color)
{
  var json="{\"cmd\":"+cmdtype_pwm+",\"intensity\":"+intesity+",\"color\":"+color+"}\n";

  myPort.write(json);
  console.log(json);
}

//gen a Temp json command to sent mcu
function cmd_temp(select)
{
  var json="{\"cmd\":"+cmdtype_temp+",\"select\":"+select+"}\n";

  myPort.write(json);
  console.log(json);
}

//ap700 cmd function
function productCheckSum(data) {
   // console.dir(data);
    var sum = 0;
    var i = 0;
    for (i = 0; i < data.length; i++)
        sum += data[i];
    return  (0x100 - sum) & 0xFF ;
 }


function  merge_checksum( sentdata,  checksum) {
    var data =  [sentdata.length+3];
   // System.arraycopy(sentdata, 0, data, 1, sentdata.length);
    for (var i=0;i<sentdata.length;i++)
    {
        data[i+1]=sentdata[i];
    }
    var b=new Buffer(2);
    b[0]=0xA9;
    b[1]=0x5C;

    data[0] = b[0];
    data[sentdata.length + 1] = checksum;
    data[sentdata.length + 2] = b[1];

    return data;
}

function culmessageLength( data) {
      return data.length+1;
}

function mergerLenght( sentdata) {
  var data = [sentdata+1];
  try {

    data[0] = culmessageLength(sentdata);
    //console.dir(data);
    for (var i = 0; i < sentdata.length; i++) {
      data[i + 1] =sentdata[i];
    }
  } catch ( e) {

  }

  return data;
}

//get Sent Command
function getSentByte(data) {

  //console.dir(data);
  data = mergerLenght(data);
  //console.dir(data);
  var checksum = productCheckSum(data);
  data = merge_checksum(data, checksum);

  return data;
}

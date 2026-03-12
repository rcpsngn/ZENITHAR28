console.log("matrix çalıştı")
const canvas = document.getElementById("matrix");
const ctx = canvas.getContext("2d");

/* CANVAS FULLSCREEN */

let fontSize = 16;
let columns;
let drops = [];
const letters = "01022026"; /*burdan matrix arka planının iç yazısı değişiyor */

function resizeCanvas(){

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

columns = Math.floor(canvas.width / fontSize);
drops = [];

for(let i = 0; i < columns; i++){
drops[i] = 1;
}

}

resizeCanvas();
window.addEventListener("resize", resizeCanvas);


/* MATRIX DRAW */

function draw(){

/* ARKA PLAN (DAHA FERAHTI) */

ctx.fillStyle = "rgba(20,40,35,0.15)";
ctx.fillRect(0,0,canvas.width,canvas.height);

/* MATRIX RENGİ */

ctx.fillStyle = "#d4af37";
ctx.font = fontSize + "px monospace";

for(let i = 0; i < drops.length; i++){

const text = letters[Math.floor(Math.random()*letters.length)];

ctx.fillText(text, i * fontSize, drops[i] * fontSize);

if(drops[i] * fontSize > canvas.height && Math.random() > 0.975){
drops[i] = 0;
}

drops[i]++;

}

}

/* ANİMASYON HIZI */

setInterval(draw, 55);
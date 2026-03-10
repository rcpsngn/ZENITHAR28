/* USER DROPDOWN */

function toggleMenu(){

const menu = document.getElementById("userDropdown")

if(menu.style.display === "block"){
menu.style.display = "none"
}else{
menu.style.display = "block"
}

}

/* CLICK OUTSIDE CLOSE */

window.onclick = function(event){

if(!event.target.closest('.user-menu')){

const menu = document.getElementById("userDropdown")

if(menu){
menu.style.display = "none"
}

}

}

/* DARK MODE */

function toggleDarkMode(){

document.body.classList.toggle("dark-mode")

localStorage.setItem(
"darkmode",
document.body.classList.contains("dark-mode")
)

}

/* LOAD DARK MODE */

if(localStorage.getItem("darkmode") === "true"){

document.body.classList.add("dark-mode")

}

/* ZENITHAR AI PANEL */

const aiBtn = document.querySelector(".ai-btn")

if(aiBtn){

aiBtn.onclick = function(){

alert("ZENITHAR AI yakında aktif olacak")

}

}

/* CHARTS */

const revenueCanvas = document.getElementById("revenueChart")

if(revenueCanvas){

new Chart(revenueCanvas,{

type:"line",

data:{
labels:["Ocak","Şubat","Mart","Nisan","Mayıs","Haziran"],

datasets:[{
label:"Gelir",

data:[12000,19000,15000,21000,25000,28000],

borderColor:"#3b82f6",

backgroundColor:"rgba(59,130,246,0.2)",

tension:0.4,

fill:true

}]

}

})

}

const expenseCanvas = document.getElementById("expenseChart")

if(expenseCanvas){

new Chart(expenseCanvas,{

type:"doughnut",

data:{
labels:["Maaş","Vergi","Ofis","Diğer"],

datasets:[{

data:[40,25,20,15],

backgroundColor:[
"#3b82f6",
"#f43f5e",
"#fb923c",
"#facc15"
]

}]

}

})

}

/* DASHBOARD SEARCH */

function dashboardSearch(){

let input = document
.getElementById("dashboardSearch")
.value
.toLowerCase()

let cards = document.querySelectorAll(".card,.panel")

cards.forEach(el => {

let text = el.innerText.toLowerCase()

if(text.includes(input)){
el.style.display = "block"
}else{
el.style.display = "none"
}

})

}
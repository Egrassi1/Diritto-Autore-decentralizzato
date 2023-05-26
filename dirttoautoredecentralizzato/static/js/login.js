const url = "http://127.0.0.1:8000"
window.addEventListener("load",onload)
document.getElementById("login").addEventListener("click",login)

async function onload(){

   
    if(window.ethereum)
	 {
		web3 = new Web3(window.ethereum)
	   await window.ethereum.request({ method: "eth_requestAccounts" })
     }else{window.alert("Devi avere Metamask installato sul tuo browser per poter usare questo servizio");}

}

async function login(){
     //recupero nonce casuale da firmare
  xhr = new XMLHttpRequest();
	xhr.open("GET", url+"/dirittodecent/token/?q="+ Web3.utils.toChecksumAddress(window.ethereum.selectedAddress),false);
  xhr.send(null)
	nonce = xhr.response

	console.log(nonce)
	//firma =  await window.ethereum.personal.sign(nonce,window.ethereum.selectedAddress)
	firma = await ethereum.request({
        method: 'personal_sign',
        params: [nonce,window.ethereum.selectedAddress]
      }); 
	xhr = new XMLHttpRequest();
  xhr.open("POST", url+"/dirittodecent/login/");
  xhr.setRequestHeader("Accept", "application/json");
	xhr.setRequestHeader("X-CSRFTOKEN", document.querySelector('[name=csrfmiddlewaretoken]').value)
  xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {  //status 200 
  if (xhr.readyState === 4) {
    console.log(xhr.status);
    window.location.replace(url+"/dirittodecent");
  }};

//il json inviato al backend consta della firma e del messaggio originale(nonce). Il backend controlla che il messaggio sia stato firmato 
//da un account per cui è stata aperta la richiesta di login e che il nonce corrisponda .
let data = { 
"firma": firma,
"msg": nonce
};

xhr.send(JSON.stringify(data));
}
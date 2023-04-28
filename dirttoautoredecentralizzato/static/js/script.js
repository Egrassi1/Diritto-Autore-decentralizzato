
	const url = "http://127.0.0.1:8000"
	open_menu =false;
  
    var DepositoContract;
    var Depositocontractaddress ;
	var Licenzacontract;
	var Licenzacontractaddress ;

	var cambioRip;
	var cambioDis;
	var prezzoDep;
	var web3;

	var formbtnD;
	var formbtnR;

	var Disbtn;
	var Ripbtn
	var Usbtn;

	var page = 1;
	var pagemax;

	tipo = document.getElementById("tipo")

	

	function pageup(){
		page = page+1


		if(document.getElementById("pagedown").disabled == true) {document.getElementById("pagedown").disabled = false}
		if (page >= pagemax)
		{
			document.getElementById("pageup").disabled = true
		}
		search()
	}

	function pagedown(){
		page = page-1

		if (document.getElementById("pageup").disabled == true) document.getElementById("pageup").disabled = false

		if (page <= 1)
		{
			document.getElementById("pagedown").disabled = true
		}
		search()
	}

	window.addEventListener("load",connetti)
	document.getElementById("menubutton").addEventListener("click",openNav)
	document.getElementById("search").addEventListener("click",search)
	document.getElementById("btn_dep").addEventListener("click",deposita)
	document.getElementById("ban").addEventListener("click",ban)
	document.getElementById("logout").addEventListener("click",logout)
	document.getElementById("pageup").addEventListener("click",pageup)
	document.getElementById("pagedown").addEventListener("click",pagedown)

	tipo.addEventListener("change",mode)


function mode(){

	document.getElementById("elenco").innerHTML = ""
	document.getElementById("ricerca").value = ""
	page = 1
	document.getElementById("pagedown").disabled = true
	document.getElementById("pageup").disabled = false
	search()

}

	async function connetti(){
	   if(window.ethereum)
	 {
		web3 = new Web3(window.ethereum)
		
		var xmlHttp = new XMLHttpRequest();
		xmlHttp.open( "GET", url+"/dirittocenet/script", false ); 
	   xmlHttp.send( null );
		ad = xmlHttp.responseText
	   Depositocontractaddress = ad.split(";")[0]
	   Licenzacontractaddress = ad.split(";")[1]

	   await window.ethereum.request({ method: "eth_requestAccounts" })
	  
	  .then((accounts) => {
		
		  const account = accounts[0]
		  window.ethereum.accounts = accounts
			 document.getElementById("portafoglio").innerHTML="portafoglio: "+account



			 buildTestocontract()
			 buildLicenzacontract()          
			  search()

			  DepositoContract.getPastEvents("cambioprezzoDeposito",{
              fromBlock: 0,
              toBlock: 'latest'
              },function(error, event){ 
                prezzoDep = event[event.length-1].returnValues[0]
  			  })

			Licenzacontract.getPastEvents("changeCambioRip",{
              fromBlock: 0,
              toBlock: 'latest'
              },function(error, event){ 
                cambioRip = event[event.length-1].returnValues[0]
  			  })

			Licenzacontract.getPastEvents("changeCambioRip",{
              fromBlock: 0,
              toBlock: 'latest'
              },function(error, event){ 
                cambioDis = event[event.length-1].returnValues[0]
  			  })


				window.ethereum.on('accountsChanged', function (accounts) {
					window.location.replace(url+"/dirittocenet/logout");
				})


		/*	
				let options = {
					fromBlock: 'latest',
					address: Licenzacontractaddress
				};
				
				let subscription = web3.eth.subscribe('logs', options,(err,event) => {
					if (!err) console.log(event)
				}).on("data", function(log){
					console.log(log)
				});
*/


			DepositoContract.events.cambioprezzoDeposito({
				fromBlock: 'latest'
			}, (error, event) => {
				if (error) {
					console.error(error);
				} else {
					// Access the event data				
					cambioprezzoDeposito= event.returnValues['prezzo']					
				}
			}).on("data", function(log){
				console.log(log)
			});

			Licenzacontract.events.changeCambioRip({
				fromBlock: 'latest'
			}, (error, event) => {
				if (error) {
					console.error(error);
				} else {
					// Access the event data
					cambioRip=event.returnValues['cambio']
				}
			}).on("data", function(log){
				console.log(log)
			});

			Licenzacontract.events.changeCambioDis({
				fromBlock: 'latest'
			}, (error, event) => {
				if (error) {
					console.error(error);
				} else {
					// Access the event data
					cambioDis=event.returnValues['cambio']
				}
			}).on("data", function(log){
				console.log(log)
			});
		
	   }).catch((error) => {
		  console.log(error, error.code);
	   })
	 }
	 else{
	   console.log("errore , metamask non abilitato")
	 }


	
	}

  function logout(){
	window.location.replace(url+"/dirittocenet/logout");
  }


function openNav() {

	//apre la barra di menu laterale
      if (open_menu)
      {
        document.getElementById("sidenav").classList.remove('exp')
      document.getElementById("menu").classList.remove("menuexp")
      open_menu =!open_menu;
      }else{
        document.getElementById("sidenav").classList.add('exp')
      document.getElementById("menu").classList.add("menuexp")
      open_menu=!open_menu;
      }
    }

  async function deposita(){
		
        const file = document.getElementById("filefield").files[0];
        //console.log(file);
        var id ;

        const reader = new FileReader();
		 // viene calcolato hash md del file selezionato per definire l'id corretto
          reader.onload = (event) => {
          const binaryString = event.target.result;
          const md5 = CryptoJS.MD5(CryptoJS.enc.Latin1.parse(binaryString)).toString(CryptoJS.enc.Hex);
          id = md5 
          console.log(id)
          var titolo = document.getElementById("ftitolo").value



			
			DepositoContract.methods.mint(titolo , id).estimateGas({"value": web3.utils.toWei(prezzoDep,"wei")},
			function(error, estimatedGas) {
				if(error){
					
					error =error.message.substring(error.message.indexOf("{") ,error.message.lastIndexOf("}")+1)
					error= JSON.parse(error)
					window.alert(error.data.reason)
					
				}else{
			const trans = DepositoContract.methods.mint(titolo , id).send({"value": web3.utils.toWei(prezzoDep,"wei")}).on('receipt', function(receipt){
			//una volta effettuata la transazione il file viene caricato sul backend
			$("#post-form").submit()			
          })
		  
			}
        })
	
	}
	
	// la transazione viene trasmessa solo se il file inserito ha il formato di '.txt'
	// un successivo controllo viene effettuato server-side , quallora il testo sia comunque del formato sbagliato
	// quest'ultimo viene segnalato come non autentico dal sistema di trust
	upload = file.name.substring(file.name.lastIndexOf("."))
	if(upload == ".txt" || upload != ".txt")
	{
	 await reader.readAsBinaryString(file);   
	}else{window.alert("Formato del file non accettato , usare solo .txt")}
    }
     
async function mintLicenzaRiproduzione(event)
      {
			id = event.target.id 
			causale = document.getElementById('Rcau'+id).value
			expire = document.getElementById('Rdat'+id).value
          //calcolo del costo
          expire = document.getElementById("Rdat"+id)
          var today = new Date();
          today.setHours(0,0,0)
          start = Math.floor(today.getTime() / 1000)
          var scadenza =Math.floor( new Date(expire.value).getTime()/1000)
          console.log("start: "+ start)
          console.log("expire: "+ scadenza)
          var value = (scadenza - start) * cambioRip
          console.log(value)
          value = web3.utils.BN(value)

		  Licenzacontract.methods.mintLicenzaRiproduzione(id,causale,scadenza,start).estimateGas({"value": web3.utils.toWei(value,"wei")},
			function(error, estimatedGas) {
				if(error){
					
					error =error.message.substring(error.message.indexOf("{") ,error.message.lastIndexOf("}")+1)
					error= JSON.parse(error)
					window.alert(error.data.reason)
					
				}else{
          Licenzacontract.methods.mintLicenzaRiproduzione(id,causale,scadenza,start).send({"value":web3.utils.toWei(value, "wei")})
				}
			 })
      }
  
async function mintLicenzaDistribuzione(event){
          //calcolo del costo
		  id = event.target.id 
		  causale = document.getElementById('Dcau'+id).value
		  num = document.getElementById('Dnum'+id).value
      
          value = (cambioDis*num) 
          console.log(value)

		  Licenzacontract.methods.mintLicenzaDistribuzione(id,causale,num).estimateGas({"value": web3.utils.toWei(value.toString(),"wei")},
			function(error, estimatedGas) {
				if(error){
					
					error =error.message.substring(error.message.indexOf("{") ,error.message.lastIndexOf("}")+1)
					error= JSON.parse(error)
					window.alert(error.data.reason)
					
				}else{
          Licenzacontract.methods.mintLicenzaDistribuzione(id,causale,num).send({"value" : web3.utils.toWei(value.toString(), "wei") })
				}})
  
      }



async function ban(){
	target= document.getElementById("banuser").value
	DepositoContract.methods.ban(target).estimateGas(function(error, estimatedGas) {
		if(error){
			error =error.message.substring(error.message.indexOf("{") ,error.message.lastIndexOf("}")+1)
					error= JSON.parse(error)
					window.alert(error.data.reason)
		}
		else{
			
			    DepositoContract.methods.ban(target).send().on('receipt', function(receipt){
	    
				xhr = new XMLHttpRequest();
				xhr.open("POST", url+"/dirittocenet/ban/"); //???
				xhr.setRequestHeader("Accept", "application/json");
				xhr.setRequestHeader("X-CSRFTOKEN", document.querySelector('[name=csrfmiddlewaretoken]').value)
			  
				xhr.setRequestHeader("Content-Type", "application/json");
				  xhr.onreadystatechange = function () {  //status 200 
				if (xhr.readyState === 4) {
				  console.log(xhr.status);
				  window.location.replace(url+"/dirittocenet");
				}};
				let data = { 
				  "tr": receipt['transactionHash'],
				  "sender": Web3.utils.toChecksumAddress(window.ethereum.selectedAddress),
				  "target": target
				  };
			  xhr.send(JSON.stringify(data));
			  window.location.replace(url+"/dirittocenet/")
			  })
				  .catch((error) => {
						console.log(error, error.code);
			  })



		}})
	


}

async function unban(event){
	id = event.target.id 
	target= document.getElementById("t"+id).innerText


	DepositoContract.methods.unban(target).estimateGas(function(error, estimatedGas) {
		if(error){
			error =error.message.substring(error.message.indexOf("{") ,error.message.lastIndexOf("}")+1)
					error= JSON.parse(error)
					window.alert(error.data.reason)
		}
		else{
			
			    DepositoContract.methods.unban(target).send().on('receipt', function(receipt){
		
		xhr = new XMLHttpRequest();
		xhr.open("POST", url+"/dirittocenet/unban/"); 
		xhr.setRequestHeader("Accept", "application/json");
		xhr.setRequestHeader("X-CSRFTOKEN", document.querySelector('[name=csrfmiddlewaretoken]').value)
	  
		xhr.setRequestHeader("Content-Type", "application/json");
		  xhr.onreadystatechange = function () {  //status 200 
		if (xhr.readyState === 4) {
		  console.log(xhr.status);
		  window.location.replace(url+"/dirittocenet");
		}};
						  
		
		let data = { 
			"tr": receipt['transactionHash'],
			"sender": String(Web3.utils.toChecksumAddress(window.ethereum.selectedAddress)),
			"target": String(target),
			"id": id
			};
	  xhr.send(JSON.stringify(data));
	  window.location.replace(url+"/dirittocenet/")
	})

	.catch((error) => {
		  console.log(error, error.code);
	   })
	}


})

}


function listusers(){
	if (Usbtn != undefined)
	{
		Usbtn.forEach(function(but){
			but.removeEventListener('click',unban)
		})
	}

	Usbtn = document.querySelectorAll(".user")
	Usbtn.forEach(function(but){
		but.addEventListener('click',unban)
	})

}

async function search(){


	var resp =(xmlHttp) =>{
		xmlHttp.send( null );
		console.log(xmlHttp.response)
		document.getElementById("elenco").innerHTML = ""
	
	
		response = xmlHttp.response
		console.log(response)
		ind = response.indexOf(".")
	
		pagemax = response.slice(0,ind)
		res= response.slice(ind+1)
		document.getElementById("elenco").insertAdjacentHTML("afterbegin",res)
		if (pagemax > 1){
			document.getElementById("pages").classList.add("v")
		}else{
			document.getElementById("pages").classList.remove("v")
		}
		document.getElementById("pgindex").innerText= String(page)+ " di "+ String(pagemax)

	}

	const but = document.getElementById("mode")
	const query = document.getElementById("ricerca").value
	var xmlHttp = new XMLHttpRequest();
	
	switch(tipo.value){
		case "a":
			link = url+"/dirittocenet/search/?q="+ query + "&t=T"+"&p="+String(page)
			xmlHttp.open( "GET", link,  false ); 
			resp(xmlHttp)
			listTesti()
			break
		case "b":
			link = url+"/dirittocenet/search/?q="+ query + "&t=L"+"&p="+String(page)
			xmlHttp.open( "GET",link , false );
		    resp(xmlHttp)
			break
		case "c":
			link = url+"/dirittocenet/search/?q="+  query + "&t=mT"+"&p="+String(page)
			xmlHttp.open( "GET", link,  false ); 
			resp(xmlHttp)
			listTesti()
			break
		case "d":
			link = url+"/dirittocenet/search/?q="+ query + "&t=mL"+"&p="+String(page)
			xmlHttp.open( "GET",link , false );
		    resp(xmlHttp)
			break
		case "e":
			link = url+"/dirittocenet/search/?q="+ query + "&t=u"+"&p="+String(page)
			xmlHttp.open( "GET",link , false );
		    resp(xmlHttp)
			listusers()
			break

	}
}


async function listTesti() {


	if (Disbtn != undefined){
	Disbtn.forEach(function(but){
		but.removeEventListener('click',mintLicenzaDistribuzione)
	})

	Ripbtn.forEach(function(but){
		but.removeEventListener('click',mintLicenzaRiproduzione)
	})

	formbtnR.forEach(function(but){
		but.removeEventListener('click', espandiRip)
	})

	formbtnD.forEach(function(but){
		but.removeEventListener('click', espandidis)
	})
	}

	Disbtn = document.querySelectorAll(".dis")
	Disbtn.forEach(function(but){
		but.addEventListener('click',mintLicenzaDistribuzione)
	})

	Ripbtn = document.querySelectorAll(".rip")
	Ripbtn.forEach(function(but){
		but.addEventListener('click',mintLicenzaRiproduzione)
	})

	formbtnR = document.querySelectorAll(".lic-btn.R")
	formbtnR.forEach(function(but){
		but.addEventListener('click', espandiRip)
	})

	formbtnD =  document.querySelectorAll(".lic-btn.D")
	formbtnD.forEach(function(but){
		but.addEventListener('click', espandidis)
	})
	  }
  
  
function espandiRip(event){
	//gli element di ciascuna card costituente il testo sono identificati tramite id composto da una nome che identifica
	// l'element(bottone , label ,etc.) + id univoco del testo depositoato
id = event.target.id
const idRip= "R"+id //bottone per la licenza di riproduzione
const idDis = "D"+id //bottone per la licenza di distribuzione
const idData = "Rdat"+id //input type data per la data di scadenza della licenza di riproduzione
const idCau = "Rcau"+id //causale
const idCos = "Rcos"+id //label che indica il costo stimato per l'acquisto della licenza

const containerRip = document.getElementById(idRip)
const containerDis = document.getElementById(idDis)
const costo = document.getElementById(idCos)
const dateInput =  document.getElementById(idData)

if (containerDis.classList.contains('expanded')){ containerDis.classList.remove('expanded');}

  if (!containerRip.classList.contains('expanded')) {
    containerRip.classList.add('expanded');
  } else {
    containerRip.classList.remove('expanded');
  }

  dateInput.addEventListener('change',()=>{

var today = new Date();
today.setHours(0,0,0)
start = today.getTime() / 1000
console.log(start)
var scadenza = new Date(dateInput.value).getTime()/1000
var value = Math.floor(scadenza - start) * cambioRip

if(value >0 ){costo.innerHTML= "costo : "+value +"WEI"}
})

}

function espandidis(event){

id = event.target.id
const idRip= "R"+id
const idDis = "D"+id
const idNum = "Dnum"+id //input type per il numero di copie autorizzato dalla licenza di distribuzione
const idCau = "Dcau"+id
const idCos = "Dcos"+id


const containerRip = document.getElementById(idRip)
const containerDis = document.getElementById(idDis)

const costo = document.getElementById(idCos)
const numberInput =  document.getElementById(idNum)


if (containerRip.classList.contains('expanded')){ containerRip.classList.remove('expanded');}

  if (!containerDis.classList.contains('expanded')) {
    containerDis.classList.add('expanded');
  } else {
    containerDis.classList.remove('expanded');
  }

  numberInput.addEventListener('change', () => {
    value = numberInput.value * cambioDis
    if(value >0 ){costo.innerHTML= "costo : "+value +"WEI"}

});

}



//seguono due metodi che vencono usati per costruire le istanze dei due contratti, tramite l'ABI del codice solidity , 
//il contract address dei contratti e il portafoglio metamask interagente  (i.e. l'utente loggato)

function buildTestocontract(){
     DepositoContract = new web3.eth.Contract(
		[
			{
				"inputs": [
					{
						"internalType": "uint256",
						"name": "prezzo",
						"type": "uint256"
					}
				],
				"stateMutability": "nonpayable",
				"type": "constructor"
			},
			{
				"anonymous": false,
				"inputs": [
					{
						"indexed": true,
						"internalType": "address",
						"name": "sender",
						"type": "address"
					},
					{
						"indexed": false,
						"internalType": "string",
						"name": "token_id",
						"type": "string"
					},
					{
						"indexed": false,
						"internalType": "string",
						"name": "titolo",
						"type": "string"
					},
					{
						"indexed": false,
						"internalType": "uint256",
						"name": "data",
						"type": "uint256"
					}
				],
				"name": "Deposito",
				"type": "event"
			},
			{
				"anonymous": false,
				"inputs": [
					{
						"indexed": true,
						"internalType": "address",
						"name": "sender",
						"type": "address"
					},
					{
						"indexed": true,
						"internalType": "address",
						"name": "target",
						"type": "address"
					}
				],
				"name": "banevent",
				"type": "event"
			},
			{
				"anonymous": false,
				"inputs": [
					{
						"indexed": false,
						"internalType": "uint256",
						"name": "prezzo",
						"type": "uint256"
					}
				],
				"name": "cambioprezzoDeposito",
				"type": "event"
			},
			{
				"anonymous": false,
				"inputs": [
					{
						"indexed": true,
						"internalType": "address",
						"name": "sender",
						"type": "address"
					},
					{
						"indexed": true,
						"internalType": "address",
						"name": "target",
						"type": "address"
					}
				],
				"name": "unbanevent",
				"type": "event"
			},
			{
				"stateMutability": "payable",
				"type": "fallback"
			},
			{
				"inputs": [
					{
						"internalType": "address",
						"name": "target",
						"type": "address"
					}
				],
				"name": "ban",
				"outputs": [],
				"stateMutability": "nonpayable",
				"type": "function"
			},
			{
				"inputs": [
					{
						"internalType": "string",
						"name": "id",
						"type": "string"
					}
				],
				"name": "idOfTesto",
				"outputs": [
					{
						"components": [
							{
								"internalType": "string",
								"name": "titolo",
								"type": "string"
							},
							{
								"internalType": "uint256",
								"name": "time",
								"type": "uint256"
							},
							{
								"internalType": "string",
								"name": "token_id",
								"type": "string"
							}
						],
						"internalType": "struct testo",
						"name": "t",
						"type": "tuple"
					}
				],
				"stateMutability": "view",
				"type": "function"
			},
			{
				"inputs": [
					{
						"internalType": "string",
						"name": "titolo",
						"type": "string"
					},
					{
						"internalType": "string",
						"name": "token_id",
						"type": "string"
					}
				],
				"name": "mint",
				"outputs": [],
				"stateMutability": "payable",
				"type": "function"
			},
			{
				"inputs": [
					{
						"internalType": "string",
						"name": "token",
						"type": "string"
					}
				],
				"name": "onwnerOf",
				"outputs": [
					{
						"internalType": "address payable",
						"name": "owner",
						"type": "address"
					}
				],
				"stateMutability": "view",
				"type": "function"
			},
			{
				"inputs": [],
				"name": "owner",
				"outputs": [
					{
						"internalType": "address",
						"name": "",
						"type": "address"
					}
				],
				"stateMutability": "view",
				"type": "function"
			},
			{
				"inputs": [
					{
						"internalType": "uint256",
						"name": "prezzo",
						"type": "uint256"
					}
				],
				"name": "setprezzoDeposito",
				"outputs": [],
				"stateMutability": "nonpayable",
				"type": "function"
			},
			{
				"inputs": [
					{
						"internalType": "address",
						"name": "owner",
						"type": "address"
					}
				],
				"name": "testiOf",
				"outputs": [
					{
						"components": [
							{
								"internalType": "string",
								"name": "titolo",
								"type": "string"
							},
							{
								"internalType": "uint256",
								"name": "time",
								"type": "uint256"
							},
							{
								"internalType": "string",
								"name": "token_id",
								"type": "string"
							}
						],
						"internalType": "struct testo[]",
						"name": "testi",
						"type": "tuple[]"
					}
				],
				"stateMutability": "view",
				"type": "function"
			},
			{
				"inputs": [
					{
						"internalType": "address",
						"name": "target",
						"type": "address"
					}
				],
				"name": "unban",
				"outputs": [],
				"stateMutability": "nonpayable",
				"type": "function"
			},
			{
				"inputs": [
					{
						"internalType": "string",
						"name": "token_id",
						"type": "string"
					}
				],
				"name": "validDeposito",
				"outputs": [
					{
						"internalType": "bool",
						"name": "validity",
						"type": "bool"
					}
				],
				"stateMutability": "view",
				"type": "function"
			},
			{
				"inputs": [
					{
						"internalType": "address",
						"name": "target",
						"type": "address"
					},
					{
						"internalType": "address",
						"name": "author",
						"type": "address"
					}
				],
				"name": "validUser",
				"outputs": [
					{
						"internalType": "bool",
						"name": "valid",
						"type": "bool"
					}
				],
				"stateMutability": "nonpayable",
				"type": "function"
			},
			{
				"stateMutability": "payable",
				"type": "receive"
			}
		],Depositocontractaddress,{from: window.ethereum.selectedAddress})
    }

function buildLicenzacontract()
    {
			 Licenzacontract = new web3.eth.Contract([
	{
		"inputs": [
			{
				"internalType": "address payable",
				"name": "addTesti",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "cambioRip",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "cambioDis",
				"type": "uint256"
			}
		],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "bool",
				"name": "tipo",
				"type": "bool"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "proprietario",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "autore",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "testo",
				"type": "string"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "id_testo",
				"type": "string"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "time",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "bytes20",
				"name": "id",
				"type": "bytes20"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "dati",
				"type": "uint256"
			}
		],
		"name": "RilascioLicenza",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "cambio",
				"type": "uint256"
			}
		],
		"name": "changeCambioDis",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "cambio",
				"type": "uint256"
			}
		],
		"name": "changeCambioRip",
		"type": "event"
	},
	{
		"stateMutability": "payable",
		"type": "fallback"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "token_id",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "causale",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "copie",
				"type": "uint256"
			}
		],
		"name": "mintLicenzaDistribuzione",
		"outputs": [],
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "token_id",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "causale",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "expire",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "start",
				"type": "uint256"
			}
		],
		"name": "mintLicenzaRiproduzione",
		"outputs": [],
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "owner",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "copie",
				"type": "uint256"
			}
		],
		"name": "priceDistribuzione",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "prezzo",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "expire",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "start",
				"type": "uint256"
			}
		],
		"name": "priceRiproduzione",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "prezzo",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "target",
				"type": "uint256"
			}
		],
		"name": "setcambioDistribuzione",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "target",
				"type": "uint256"
			}
		],
		"name": "setcambioRiproduzione",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address payable",
				"name": "_to",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "_amount",
				"type": "uint256"
			}
		],
		"name": "transfer",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"stateMutability": "payable",
		"type": "receive"
	}
], Licenzacontractaddress,{from: window.ethereum.selectedAddress})
    }

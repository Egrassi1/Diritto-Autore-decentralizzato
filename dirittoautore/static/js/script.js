
	open_menu =false;
    var _event;

    var DepositoContract;
    var Depositocontractaddress ;
	var Licenzacontract;
	var Licenzacontractaddress ;

	var cambioRip;
	var cambioDis;
	var prezzoDep;
	var web3;

	async function connetti(){
		


	   if(window.ethereum)
	 {
		web3 = new Web3(window.ethereum)
		
		var xmlHttp = new XMLHttpRequest();
		xmlHttp.open( "GET", "http://127.0.0.1:8000/dirittocenet/script", false ); 
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
             listTesti()

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
					window.location.replace("http://127.0.0.1:8000/dirittocenet/logout");
				})
		
	   }).catch((error) => {
		  console.log(error, error.code);
	   })
	 }
	 else{
	   console.log("errore , metamask non abilitato")
	 }
	}

  function logout(){
	window.location.replace("http://127.0.0.1:8000/dirittocenet/logout");
  }

  function selectmode(){
	//questa funzione  cambia dalla modalità visualizzazione licenza a quella visualizzazione testi depositati e viceversa

	const but = document.getElementById("mode")
	document.getElementById("elenco").innerHTML = ""
	if(but.innerHTML == "visualizza le tue licenze")
	{
		but.innerHTML = "visualizza i testi depositati"
		listLicenze()

	}else{
		but.innerHTML = "visualizza le tue licenze" 
		listTesti()
}
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
     
      async function mintLicenzaRiproduzione(id , causale, expire)
      {
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
  
      async function mintLicenzaDistribuzione(id,causale,num){
          //calcolo del costo
          console.log(id)
          console.log(causale)
      
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
	DepositoContract.methods.ban(target).send()
	.catch((error) => {
		  console.log(error, error.code);
	   })
}

async function unban(){
	target= document.getElementById("unbanuser").value
	DepositoContract.methods.unban(target).send()
	.catch((error) => {
		  console.log(error, error.code);
	   })
}


async function search(){
	const but = document.getElementById("mode")
	const query = document.getElementById("ricerca").value
	var xmlHttp = new XMLHttpRequest();
	if(but.innerHTML == "visualizza le tue licenze")
	{
    xmlHttp.open( "GET", "http://127.0.0.1:8000/dirittocenet/search/?q="+ query + "&t=T", false ); 
	}else{
		xmlHttp.open( "GET", "http://127.0.0.1:8000/dirittocenet/search/?q="+ query + "&t=L", false );
	}
	xmlHttp.send( null );
	console.log(xmlHttp.response)
	document.getElementById("elenco").innerHTML = ""
	document.getElementById("elenco").insertAdjacentHTML("afterbegin",xmlHttp.response)

}


async function listTesti() {

	var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", "http://127.0.0.1:8000/dirittocenet/search/?q=&t=T", false ); 
    xmlHttp.send( null );
	document.getElementById("elenco").innerHTML = ""
	document.getElementById("elenco").insertAdjacentHTML("afterbegin",xmlHttp.response)
	  }
  
async function listLicenze(){

	var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", "http://127.0.0.1:8000/dirittocenet/search/?q=&t=L", false ); 
    xmlHttp.send( null );
	document.getElementById("elenco").innerHTML = ""
	document.getElementById("elenco").insertAdjacentHTML("afterbegin",xmlHttp.response)
    }
  
function espandiRip(id){
	//gli element di ciascuna card costituente il testo sono identificati tramite id composto da una nome che identifica
	// l'element(bottone , label ,etc.) + id univoco del testo depositoato

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

function espandidis(id){

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

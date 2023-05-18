// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;
import "testo.sol";

enum TipoLicenza {RIPRODUZIONE,DISTRIBUZIONE}

  // struttura base della licenza
  struct Licenza{
    bytes20 id;
    testo t ;
    string causale;
    TipoLicenza _tipoLicenza;
    uint256 timestamp;
    uint256 start;
    uint256 expire;
    uint copievendute;
  }


contract LicenzaSiae{

address public owner;



  DepositoTesti dt;
 
  uint cambioRiproduzione = 10000000;
  uint cambioDistribuzione = 10000000;
  uint totalLicenze;

  event changeCambioRip(uint cambio);
  event changeCambioDis(uint cambio);


  mapping(address => Licenza[]) addressToLicenza;

  modifier ownerOnly(){
      require(msg.sender == owner);
      _;
}

 event RilascioLicenza(bool tipo , address indexed proprietario, address indexed autore, string testo ,string id_testo,uint time, bytes20 id,uint dati);

 constructor( address payable addTesti,uint cambioRip,uint cambioDis) {
 dt = DepositoTesti(addTesti);
 owner = msg.sender;
 setcambioDistribuzione(cambioDis);
 setcambioRiproduzione(cambioRip);
}

function mintLicenzaRiproduzione(string memory token_id, string memory causale, uint expire,uint start) payable external 
{

  testo memory t = dt.idOfTesto(token_id);
  uint value = priceRiproduzione(expire,start);
  address autore = dt.onwnerOf(token_id);
  require (msg.value == value,"Ether non sufficienti a effettuare la transazione");
  require(validLicenzaRiproduzione(msg.sender,expire,t),"Esiste gia' una licenza di riproduzione valida");
  require(dt.validUser(msg.sender, autore ), "l'utente non e' abilitato dall'autore ad acquistare la licenza");

  uint timestamp = block.timestamp;
  bytes20 _id = bytes20(keccak256(abi.encodePacked(msg.sender, blockhash(block.number - 1))));
  Licenza memory _licenza = Licenza(_id,t,causale,TipoLicenza.RIPRODUZIONE,timestamp,start,expire,0);

  addressToLicenza[msg.sender].push( _licenza) ;

  emit RilascioLicenza(true,msg.sender,autore,t.titolo,token_id,timestamp,_id,expire);
  transfer(dt.onwnerOf(token_id), value/2);
}


function mintLicenzaDistribuzione(string memory token_id, string memory causale, uint copie) payable external
{
 testo memory t = dt.idOfTesto(token_id);
 uint value = priceDistribuzione(copie);
  address autore = dt.onwnerOf(token_id);

 require(msg.value == value,"Ether non sufficienti a effettuare la transazione");
 require  (dt.validUser(msg.sender, autore), "l'utente non e' abilitato dall'autore ad acquistare la licenza");
 
 uint timestamp = block.timestamp;
 bytes20 _id = bytes20(keccak256(abi.encodePacked(msg.sender, blockhash(block.number - 1))));
 Licenza memory _licenza = Licenza(_id,t,causale,TipoLicenza.DISTRIBUZIONE,timestamp,0,0,copie);

 addressToLicenza[msg.sender].push( _licenza) ;

 emit RilascioLicenza(false,msg.sender,autore,t.titolo,token_id,timestamp,_id,copie);
 transfer(dt.onwnerOf(token_id), value/2);

}

// verifica che non ci siano altre licenze di riproduzione 
//attive sulle stesso testo e con expire Date minore o uguale di quella che si intende compraare
function validLicenzaRiproduzione(address buyer , uint expire,testo memory t) internal view returns(bool valid)
{
  for (uint i=0; i<addressToLicenza[buyer].length; i++){
    if(addressToLicenza[buyer][i]._tipoLicenza == TipoLicenza.RIPRODUZIONE)
    {
    testo memory t1 = addressToLicenza[buyer][i].t;
   
    if((keccak256(abi.encodePacked(t1.token_id)) ==keccak256(abi.encodePacked(t.token_id))) && addressToLicenza[buyer][i].expire >= expire )
    {
      return false;
    }
    }
  }
  return true;
}

 // questa funzione calcola il prezzo della licenza di dstribuzione
function priceRiproduzione(uint expire,uint start) public view returns (uint prezzo){
  return ((expire-start) * cambioRiproduzione) * 1 wei;
}

function priceDistribuzione(uint copie) public view returns (uint prezzo)
{
  return (copie *  cambioDistribuzione) * 1 wei;
}

 // Questa funzione trasferisce ether all'indirizzo passato come parametro
    function transfer(address payable _to, uint _amount) public {
        (bool success, ) = _to.call{value: _amount}("");
        require(success, "Ether non sufficienti");
    }


function setcambioRiproduzione(uint target) ownerOnly public {
   cambioRiproduzione = target;
   emit changeCambioRip(target);
}

function setcambioDistribuzione(uint target) ownerOnly public {
   cambioDistribuzione = target;
   emit changeCambioDis(target);
}
  receive() external payable {}
  fallback() external payable {}

}
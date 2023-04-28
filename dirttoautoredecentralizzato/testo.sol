// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

// struttura del token
  struct  testo{
        string titolo;
        uint time; 
        string token_id;
        //uri della risorsa
    }



contract DepositoTesti{

  address public owner;
  uint totalsupply;
  mapping (address =>  testo []) TestiPosseduti;  //testi depositati per autore 

  mapping(string => testo) idToTesto;  //testo depositato per id

  mapping(string => address) idToAutore;

  mapping(address => address[]) banned ; // portafogli bannati dall'autore

  uint prezzoDeposito;

 event Deposito(address indexed sender,string  token_id,string titolo, uint data);    
 event cambioprezzoDeposito(uint prezzo);

 event banevent (address indexed sender, address indexed target);
 event unbanevent (address indexed sender, address indexed target);

 constructor(uint prezzo) 
{
  owner = msg.sender;
 setprezzoDeposito(prezzo);
 
 emit cambioprezzoDeposito(prezzo);
}

modifier ownerOnly(){
      require(msg.sender == owner);
      _;
}

  // funzione di deposito di un testo
        function mint(string calldata titolo , string calldata token_id) payable external  {
            require(validDeposito(token_id), "Un testo con lo stesso id e' gia' stato depositato");
            require(msg.value == prezzoDeposito, "Ether non sufficienti a effettuare la transazione"); // prezzo per il deposito del testo
            testo  memory t = testo(titolo,block.timestamp ,token_id);

            TestiPosseduti[msg.sender].push(t);
            idToAutore[token_id] = msg.sender;
            idToTesto[token_id] = t;
           
            totalsupply = totalsupply+1;

            emit Deposito(msg.sender, t.token_id,t.titolo,t.time);
    
        }

// controlla se il file da depositare è valido
function validDeposito(string calldata token_id) public view returns(bool validity)
{
  if(onwnerOf(token_id) == address(0)){return true;}
  else return false;
}
  //view dei testi a partire dall'user
    function testiOf(address owner) public view returns (testo[] memory testi)
    {
        return TestiPosseduti[owner];
    }
  //view dell'user a partire dal testo
    function onwnerOf (string calldata token) public view returns (address payable owner)
    {
         return payable(idToAutore[token]);
    }
    
    function idOfTesto(string calldata id) public view returns(testo memory t)
    {
      return idToTesto[id];
    }

// fuznioni per bannare o sbannare portafogli
    function ban(address target) external{
      require(msg.sender != target, "non e' possibile bannare se stessi");
      require(validban(target), "utente gia' bannato");
      banned[msg.sender].push(target);
      emit banevent(msg.sender, target);
    }

    function validban(address target) internal view returns (bool valid){
        for(uint i = 0; i < banned[msg.sender].length ; i++ )
      {
         if(banned[msg.sender][i] == target)
        {
          return false;
        }
      }
      return true;
    }

    function unban(address target) external{


         require(validunban(target), "l'utente selezionato non e' attualmente bannato ") ;
           for(uint i = 0; i < banned[msg.sender].length ; i++ )
      {
         if(banned[msg.sender][i] == target)
        {

          banned[msg.sender][i] = banned[msg.sender][ banned[msg.sender].length -1];
          banned[msg.sender].pop();
          emit unbanevent(msg.sender, target);
        }
      }
        

    
    }


    function validunban(address target) internal view returns (bool valid){
        for(uint i = 0; i < banned[msg.sender].length ; i++ )
      {
         if(banned[msg.sender][i] == target)
        {
          return true;
        }
      }
      return false;
    }

// restituisce true se l'utente non è stato bannato dall'autore del testo 
  function validUser(address target, address author)external view returns (bool valid){

    for(uint i = 0 ; i < banned[author].length ; i++ ){

    if (banned[target][i]== target)
    {
      return false;
    }

  }
     return true;
  }


function setprezzoDeposito(uint prezzo) ownerOnly public{
  prezzoDeposito = prezzo;
  emit cambioprezzoDeposito(prezzo);
}


      receive() external payable {}
      fallback() external payable {}

}


    var userProducts = [];  
    var recommendedProducts = [];

    var user_id = 'Qh5A5NlP4UVvddSasOYR4A';
function initialise(){
   
    var user_products = "http://127.0.0.1:28017/yideas/user_product/?filter_user_id="+user_id; 
    $.ajaxSetup( { "async": false } );
    $.getJSON(user_products, function(data) {

        $.each(data.rows, function(index, item) { 
            userProducts.push(item.products); 
        }); 
    });

    // Find similar products
    var similarProducts = "http://127.0.0.1:28017/yideas/product_recommendations/"; 
    $.ajaxSetup( { "async": false } );
    $.getJSON(similarProducts, function(data) {
        $.each(data.rows, function(index, item) {  

            if( $.inArray(item.product_id, userProducts)){
                recommendedProducts.push(item.recommendations); 
            }
        }
        )
    });

    addTable1(); addTable2();
}

function addTable1(){
    addTable('myDynamicTable1', userProducts[0])
}

function addTable2(){
    addTable('myDynamicTable2', recommendedProducts[0])
}
 
function addTable(elemName, productsArray) {
      
    var myTableDiv = document.getElementById(elemName);
      
    var table = document.createElement('TABLE');
    
   
    
    var tableBody = document.createElement('TBODY');
    table.appendChild(tableBody);
      
    var tr = document.createElement('TR');
        tableBody.appendChild(tr);
        productsArray.forEach( function(s) { 
        var td = document.createElement('TD');
        td.width='75';

        var businesses = "http://127.0.0.1:28017/yideas/business/?filter_business_id="+s;
        $.ajaxSetup( { "async": false } );
        $.getJSON(businesses, function(data) {
        $.each(data.rows, function(index, item) {  
                
                description = item.name;

                var div = document.createElement('DIV');
                div.className = "card";
                var textElement = document.createTextNode(description);
                textElement.className = "title";
                div.appendChild(textElement);
            
                div.appendChild(createImage(index, s));
                td.appendChild(div);
                tr.appendChild(td);

                var tdSpace = document.createElement('TD');
                tdSpace.width='20';
                tr.appendChild(tdSpace);
        }
        )
    });

    } );

    myTableDiv.appendChild(table);
    

}

    function createImage(i, s) {
            var x = document.createElement("IMG");
            x.setAttribute("src", "reco/images/product_image" + i+ ".png");
            x.setAttribute("height", "150");
            x.setAttribute("width", "150");
            


        var productDescriptions = "http://127.0.0.1:28017/yideas/product_descriptions/?filter_product_id=" + s;
        $.ajaxSetup( { "async": false } );
        $.getJSON(productDescriptions, function(data) {
        $.each(data.rows, function(index, item) {  
            // if( s == item.product_id){
                x.setAttribute("alt", item.text);
            // }
        }
        )
    });


            return x;
        }

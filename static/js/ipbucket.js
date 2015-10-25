/*

Sources:
Jquery datatable: https://www.datatables.net/
JQuery treetable: http://ludo.cubicphuse.nl/jquery-treetable/
dot2num, dot2num: http://javascript.about.com/library/blipconvert.htm

*/

var ip_network_table, ip_domain_table, ip_address_table;

$(document).ready(function()
{  
    // Initialize HTML elements for io_network_add page
    if ($('body').hasClass('ip_domain_add'))
    {
        $('#ip_domain_add_button').click(ip_domain_add_buttonClick); 
        
    }
    if ($('body').hasClass('ip_network_add'))
    {
        ajax_call("GET",'/api/ip_domain/all', "" ,callback_ip_network_add_select);
        $('#ip_network_add_button').click(ip_network_add_buttonClick); 
    }
    
    if ($('body').hasClass('ip_network_overview'))
    {
        $("#example-basic-static").treetable({ initialState : "collapsed", expandable : true  });
        ajax_call("GET","/api/ip_network/1", "" , callback_ip_network_overview); 
    }

    if ($('body').hasClass('ip_network'))
    {
        build_ipv4_paging($("#ip").attr('value'), $("#mask").attr('value'))
        count = Math.min(Math.pow(2, 32 - $("#mask").attr('value')), 255);
        ajax_call("GET","/api/ip_address/" + $("#ip_domain_id").attr('value') + "/" + $("#ip").attr('value') + "/" + count, "", callback_ip_network); 
    }

    if ($('body').hasClass('ip_domain_overview'))
    {
        ajax_call("GET", "/api/ip_domain/overview", "" , callback_ip_domain_overview); 
    }
});




function build_ipv4_paging(ip, mask) {
    ip = parseInt(ip);
    if (mask < 24) {
        addresscount = Math.pow(2, (32 - mask));
        //alert(num2dot(ip+1))
        for( var i=0; i < addresscount; i = i + 255) {
            //alert(num2dot(ip+i) + " - " + num2dot(ip+i+255));
            $('#ip_network_paging').append($('<option>', { 
                value: ip ,
                text: num2dot(ip+i) + " - " + num2dot(ip+i+255)
            }));
            i=i+1
        }
    } 

}

function callback_ip_network_add_select(data,status) {
    data.result.forEach(function(entry) {
        $('#ip_domain').append('<option value="' + entry['id'] + '">' + entry['name']  + '</option>');
    });
}

function init_ip_domain_table(columnArray, VLANarray) {
    ip_domain_table = $('#ip_domain_table').dataTable(buildTableParameters([10,10,10,10,10], { "jQueryUI": true, "paging": false, "searching": false, "data": columnArray  , "aaSorting": [[ 1, "desc" ]]}));
    $('#ip_domain_table').DataTable().columns.adjust().draw();
    return ip_domain_table;
}

function init_ip_address_table(columnArray, VLANarray) {
    ip_address_table = $('#ip_address_table').dataTable(buildTableParameters([10,100,200,200,60,10], {  "paging": false, "data": columnArray  })).makeEditable( {
        
        "aoColumns": [
            null,
            {
                tooltip: 'Click to change hostname',
                event: 'click',
                submit: 'Ok',
                sUpdateURL: function(value, cellpos){ ip_address_update(value ,ip_address_table.fnGetPosition( this )); }
            },
            {  
                tooltip: 'Click to change description',
                event: 'click',
                submit: 'Ok',
                sUpdateURL: function(value, cellpos){ ip_address_update(value,ip_address_table.fnGetPosition( this )); }
            },
            {
                tooltip: 'Click to change reservation',
                type: 'select',
                event: 'click',
                onblur: 'cancel',
                submit: 'Ok',
                data: "{'':'Please select...', 'false':'No','true':'Yes'}",
                sUpdateURL: function(value, settings){  ip_address_update(value,ip_address_table.fnGetPosition( this )); }
            }
        ]        
    });
    $("div.toolbar").html("<select id='ip_network_paging'><option value=''>-- Choose range to modify --</option></select>");
    // class="fg-toolbar ui-toolbar ui-widget-header ui-helper-clearfix ui-corner-tl ui-corner-tr"
    $('#ip_address_table').DataTable().columns.adjust().draw();
    return ip_address_table;
}

function ip_address_update(value, cellpos)
{ 
    // cellpos[0] = row , [1] = column (hidden skipped), [2] = column (hidden not skipped)
    if (cellpos[2] == 2) data = { 'fqdn': value };
    if (cellpos[2] == 3) data = { 'description': value };
    if (cellpos[2] == 4) data = { 'reserved': (value === "true") };

    alert( $("#ip_address_table tr:eq(" + (cellpos[0]+1).toString() + ") td:eq(1)").text() + " " + dot2num($("#ip_address_table tr:eq(" + (cellpos[0]+1).toString() + ") td:eq(1)").text()));
    ip = dot2num($("#ip_address_table tr:eq(" + (cellpos[0]+1).toString() + ") td:eq(1)").text());
    //$("#ip_address_table tr:eq(" + (cellpos[0]+1).toString() + ") td:eq(0)").append('<img src="/img/ajax-loader.gif">');
    //$('#notificationarea').html('<img src="/img/ajax-loader.gif">');

    ajax_call("PUT", "/api/ip_address/" + $("#ip_domain_id").attr('value') + "/" + ip, data, callback_ip_address_update)
}



function callback_ip_address_update(data,status) 
{
    $('#notificationarea').append('<table width=800px border=1><tr><td>' + data['notification'] + '</td></tr></table>');
    ajax_call("GET", "/api/ip_address/" + $("#ip_domain_id").attr('value') + "/" + $("#ip").attr('value') + "/" + count, "", callback_ip_network); 
}


function ip_domain_add_buttonClick()
{
    var data = {};
    $.each($('#ip_domain_add_form').serializeArray(), function(i, field) {
        data[field.name] = field.value;
    });

    ajax_call("POST", "/api/ip_domain/" , data, callback_add)
}

function ip_network_add_buttonClick()
{
    var data = {};
    $.each($('#ip_network_add_form').serializeArray(), function(i, field) {
        data[field.name] = field.value;
    });

    ajax_call("POST", "/api/ip_network/" , data, callback_add)
}



function callback_add(data,status) 
{
    $('#notificationarea').html('<table width=800px border=1><tr><td>' + data['notification'] + '</td></tr></table>');
}



function callback_ip_network_overview(data,status) 
{
    var row,rows ="", parent_id="";
    var columnArray =[];

    // Prepare the rows to be added to the treetable
    for (var i=0; i < Object.keys(data.result).length; i++) {
        parent_id= ' data-tt-parent-id="' + data.result[i].parent + '"';
        row = '<tr data-tt-id="' + data.result[i].id + '"'+ parent_id + '">' 
            + '<td><a href="' + data.result[i].ip_domain_id + '/' + data.result[i].id + '">' + data.result[i].ip + '</a></td>'
            + '<td>' + data.result[i].name  + '</td>'
            + '<td>' + '</td>'
            + '<td><input type=checkbox></input></td>'
            + '</tr>';
        rows = rows + row
        parent_id =""
    }
    // Add the rows to the treetable
    $("#example-basic-static").treetable("loadBranch",null,rows);   

    // the collapseAll function does not seem to work correctly using the loadbranch approach with multiple rows
    // Instead class attributes are updated manually to relect a collapsed tree.
    $('#example-basic-static tr').each(function () {      
        if(($(this).attr('data-tt-parent-id') != 0) & ($(this).hasClass("leaf collapsed") | $(this).hasClass("branch collapsed")))
        {
            $(this).css('display', 'None');
        }
    });
};

function callback_ip_domain_overview(data,status) 
{
    var columnArray =[];
    if (ip_domain_table) ip_domain_table.fnDestroy(); // destroy the current ip_domain_table table
    for (var i=0; i < Object.keys(data.result).length; i++) {
       columnArray.push( [ data.result[i].id, data.result[i].name, data.result[i].ipv4network_count ,  data.result[i].ipv6network_count, "bla"]) ;
    }
    $("#ip_domain_table").show();  
    ip_domain_table = init_ip_domain_table(columnArray);
};

function callback_ip_network(data,status) 
{

    var columnArray =[];
    if (ip_address_table) ip_address_table.fnDestroy(); // destroy the current ip_address_table table
    for (var i=0; i < Object.keys(data.result).length; i++) {
        if (data.result[i].reserved == true) reserved = "Yes";
        else reserved = "No";
        columnArray.push( [ data.result[i].ip, data.result[i].ip_string, data.result[i].fqdn , data.result[i].ip + " " + data.result[i].description, reserved, "<input type=checkbox id='cb_ip_address_" + data.result[i].id + "'>"]) ;
    }
    $("#ip_address_table").show();  
    console.log(columnArray);
    ip_address_table = init_ip_address_table(columnArray);
};


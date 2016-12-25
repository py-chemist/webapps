$(document).ready(function(){

    var options = ['#check_boxes', '#more_options','#update_reset']

    // $.each(options, function(key, value){
    // 	$(value).hide();
    // });
    var hide_options = function(){
	$('#check_boxes').hide();
	$('#more_options').hide();
	$('#update_reset').hide();	
    };
    //hide_options();
    var last_content = "";
    var smiles_mol = "";
    var updated_content = "";
    $( "input[value='-w']" ).prop('checked', true);

    $('#search').on('click', function(){
	chemical = $('#chemical').val();
	smiles_mol = 'smiles';
	if (chemical == "")
	    { 
		alert("Please do not leave this field blank");
	    }
	else {
	    $.ajax({
		type: "POST",
		url: "/mol_2_chemfig/get_smiles",
		contentType: 'application/json; charset=UTF-8',
		data: JSON.stringify({'chemical': chemical}),	    
		dataType: 'json',
		success: function(data){
		    if(data.smiles == "Not found"){
			var text = chemical + ' not found in the database. Please use the sketcher to draw your molecule.';
			$('#warning').html(text);
			$('#not_found').css('display', 'block');
		    } else{
			$('#txt_area').val(data.smiles);
			$('#chemical').val("");
		    }
		}, error: function(error){
		    alert(error);
		}
	    });
	}
	smiles_mol = '';
    });   
		   

    $('#convert').on('click', function(){
	var data = $("#txt_area").val();
	if(data.indexOf('chemfig') != -1){
	    var text = "It looks like you are trying to convert chemfig format to chemfig format." +
		  "\n" +
		"Please select options and use 'Apply' button to modify the current structure"
	    $('#warning').html(text);
	    $('#not_found').css('display', 'block');
	} else{
	    last_content = data;
	    $.ajax({
		type: "POST",
		url: '/mol_2_chemfig/smiles_to_chemfig',
		contentType: 'application/json; charset=UTF-8',
		data: JSON.stringify({'data': data,
				      'smiles_mol': smiles_mol}),	    
		dataType: 'json',
		success: function(results){
		    if(results.pdflink == "Chemfig cannot be generated"){
			var warning = "Oops.. Chemfig cannot be generated. Please check the structure for errors (e.g. a 5-valence carbon)";
			$('#warning').html(warning);
			$('#not_found').css('display', 'block');
		    }
		    else{
			$('#txt_area').val(results.chemfig);
			$("#pdf").attr('src', results.pdflink);
			$('#check_boxes').show();
			$('#more_options').show();
			$('#update_reset').show();
		    }
		},
		error: function(error){
		    console.log(error);
		}
		
	    });
	 }
    });

    var update = function(link){
	updated_content = $("#txt_area").val();
	var chbx=[];		
	    $('input[name="check"]:checked').each(function () {
		chbx.push(this.value);
	    });
	if(chbx.indexOf('-rm') != -1 & chbx.indexOf('-j') != -1 ){
	    var warning = 'Please select either "inline" or "remove %" checkbox but not both.';
	    $('#warning').html(warning);
	    $('#not_found').css('display', 'block');
	    // angular.element(document.querySelector('#warning')).html(warning);
	    // document.getElementById('not_found').style.display='block';
	} else{
	    angle = $('input[name="angle"]').val();
	    hydrogens = $('#H2 :selected').text();
	    $.ajax({
		type: "POST",
		url: "/mol_2_chemfig/" + link,
		contentType: 'application/json; charset=UTF-8',
		data: JSON.stringify({'last_content': last_content, "angle": angle,
				      'hydrogens': hydrogens, "chbx": chbx}),
		dataType: 'json',
		success: function(results){
		    $('#txt_area').val(results.chemfig);
		    $("#pdf").attr('src', results.pdflink);
		},
		error: function(error){
		    alert(error);
		}
	    });
	}
    };

    $('#check_update').on('click', function(){
	update("apply");
    });

    $('#check_reset').on('click', function(){
        $('input[name="check"]').attr('checked', false);
	$( "input[value='-w']" ).prop('checked', true);    
        $('input[name="angle"]').val('0.0');
        $('#H2').val('keep');
	update("apply");
    });

    $("#txt_area").keyup(function(e){
	
	// Making sure it applies to chemfig format only, not to smiles or mol format.
	if ($("#txt_area").val().indexOf("chemfig") != -1)
	   {
	//     // Ignoring Shift and arrows key in live update
	    var code = (e.keyCode || e.which);
	    if(code == 16 || code == 32 || code == 37 || code == 38 || code == 39 || code == 40 ) {
		return;
	    }
	   }
	    smiles_mol = $("#txt_area").val();
	    $.ajax ({
		type: "GET",
		url: "/mol_2_chemfig/update",
		data: {"smiles_mol": smiles_mol},		    
		success: function(result){
		    if (result.pdf_link == 'pdf generation foobared')
		    {
			$("#pdf").attr('src', "websites/mol_2_chemfig/static/files/broken.pdf"); 
		    }
		    else{
			$("#pdf").attr('src', result.pdflink);
		    }			
		},
		error: function(error) {
		    console.log(error)
		}
	    });
    });
    
});

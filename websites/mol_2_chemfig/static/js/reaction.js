$( document ).ready(function() {
    
    var text_above_arrow = [];
    var text_bellow_arrow = [];
    
    var hide_elements = ["#sketcher2_button_scale_plus", "#sketcher2_button_scale_minus",
			 "#sketcher2_button_open", "#sketcher2_button_save",
			 "#sketcher2_buttons_attribute"];

    $.each(hide_elements, function(index, value){
	$(value).hide();
    });

    // Set id for sketcher toolbar
    $('div[style="font-size:10px;"]').attr('id', 'sketcher_toolbar');
    $('#sketcher_toolbar').append($("<input>", {id: "arrow_text", type: "text",
						class: "w3-round",
    					       placeholder: "text above arrow; text below arrow"}));
    // $('#sketcher_toolbar').append($("<input/>", {id: "add_text",
    // 						 type: "button",
    // 						 class:"w3-btn w3-indigo w3-tiny w3-round",
    // 						 value: "Add text"}));

    $('#convert2').on('click', function(){
	var molecules = sketcher2.molecules;
        var shapes = sketcher2.shapes;
	var reaction = JSON.stringify(new ChemDoodle.io.JSONInterpreter().contentTo(molecules, shapes));
	var input_text = $("#arrow_text").val();
        //alert(JSON.stringify($('sketcher_canvas').children()));
	// alert(reaction);
        var num_of_molecules = Object.keys(molecules).length;
        var MOLFiles = [];
        for(var i = 0; i < num_of_molecules; i ++){
            var molFile = ChemDoodle.writeMOL(molecules[i]);
            MOLFiles.push(molFile);
        };
	$.ajax({
            type: "POST",
            url: "/mol_2_chemfig/convert_reaction",
            contentType: 'application/json; charset=UTF-8',
            data: JSON.stringify({'MOLFiles': MOLFiles,
                                  'reaction': reaction,
				  'input_text': input_text}),
            dataType: 'json',
            success: function(data){
                $('#reaction').val(data.data); 
                $("#pdf").attr('src', data.pdflink);
            },            
            error: function(error){
                console.log(error);
            },
        });
    });
    
    

    $(document).keyup(function (e) {
	if ($("#arrow_text:focus") && (e.keyCode === 13)) {
            var input_text = $("#arrow_text").val();
            var molecules = sketcher2.molecules;
            var shapes = sketcher2.shapes;
	    // alert(JSON.stringify(new ChemDoodle.io.JSONInterpreter().contentTo(molecules,shapes)));
	    // alert(JSON.stringify(shapes));
            var num_of_arrows = shapes.length;
            var all_text = input_text.split('|');
	    // alert(input_text);
	    
            for(var i = 0; i < num_of_arrows; i++){
		var arrow_text = all_text[i].split(";");
                shapes[i].topText = arrow_text[0];
	        text_above_arrow.push(arrow_text[0]);
                shapes[i].bottomText = arrow_text[1];
		text_bellow_arrow.push(arrow_text[1]);
            }
            sketcher2.loadContent(molecules, shapes);
	}
   });	
});

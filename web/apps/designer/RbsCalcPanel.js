
/*
  TODO: this shouldn't be an instance. it should be instantiatable
        as it is now, if you close the tab, and re-open, it won't work.
 */

var rbs_calculate_input_textarea = new Ext.form.TextArea({
        id: 'rbs_calculate_input_textarea',
        fieldLabel: 'Sequence',
        width: 300,
        height: 100
    });


var rbs_calculate_output_textarea = new Ext.form.TextArea({
        id: 'rbs_calculate_output_textarea',
        fieldLabel: 'Result',
        width: 300,
        height: 100
    });


var RbsCalcPanel = new Ext.FormPanel({
        labelWidth: 75,
        title: 'RBS Calculator',
        closable: true,
        frame: true,
        header: false,
        bodyStyle: 'padding:5px',
        width: 400,
        defaultType: 'textfield',
        items: [
                rbs_calculate_input_textarea,
                rbs_calculate_output_textarea,
                {
                    xtype: 'textfield',
                    fieldLabel: "Start codon offset (0-indexed)",
                    id: 'rbs_calculate_start_codon_offset'
                },
                ],
        buttons: [{
                text: 'Calculate (Voigt)',
                listeners: {
                    click: function(n) {
                        rbs_calculate();
                    }
                }
            }, {
                text: 'Cancel',
                listeners: {
                    click: function(n) {
                        cancel_rbs_calculate();
                    }
                }
            }]
              
    });  

function rbs_calculate() {

    var seq = $('rbs_calculate_input_textarea').value;

    if(!seq || (seq == '')) {
        alert("You need to specify a sequence in the input field.");
        return false;
    }

    var json_str = Object.toJSON({
            sequence: seq
        });

    new Ajax.Request(RBS_CALCULATE_URL, {
            method: 'post',
            encoding: 'UTF-8',
            parameters: {
                json: json_str
                    },
            onSuccess: rbs_calculate_got_result,
            onFailure: rbs_calculate_error
    });


}

function rbs_calculate_got_result(response) {
    if(!response.responseText) {
        alert("An error occurred during rbs calculation."); // TODO better error reporting
    }
    var resp = response.responseText.evalJSON();

    $('rbs_calculate_output_textarea').value = resp.output;
}

function rbs_calculate_error(response) {
    // TODO better error reporting
    alert("An error occurred during rbs calculation: " + response.responseText);
    return false;
}

/*
 * 
 * File: AssemblerPanel.js
 *
 */

AssemblerPanel = Ext.extend(AssemblerPanelUi, {
	partInstances: [],
	annealerURL: SERVICE_PATH_ANNEALER,
	assemblerURL: SERVICE_PATH_ASSEMBLER,
	shouldAnneal: false,
	//savePlanButton: null,
	
	initComponent: function() 
	{
		var button;
	
		AssemblerPanel.superclass.initComponent.call(this);
	
		var selectionModel = this.planGridPanel.getSelectionModel();
		selectionModel.on('cellselect', this.insertBinCellSelectHandler, this);
	
		var selectionModel = this.constructsEditorGrid.getSelectionModel();
		selectionModel.on('rowselect', this.constructsGridRowSelectHandler, this);
	
		this.assembleButton.setHandler(this.assembleButtonClickHandler, this);
		this.emptyBinButton.setHandler(this.emptyBinButtonClickHandler, this);
		this.constructsCSVButton.setHandler(this.constructsCSVButtonClickHandler, this);
	
		this.feedbackTextArea.setValue("The Assembler is ready.\n");
	
	//	button = new Ext.ux.Exporter.Button({
	//		store: this.planGridPanel.getStore(),
	//		text: "Spreadsheet"
	//	});
	//	
	//	this.planPanel.getTopToolbar().add(button);
	
	//	button = new Ext.ux.Exporter.Button({
	//		exportFunction: 'exportStore',
	//		store: this.constructsEditorGrid.getStore(),
	//		text: "Spreadsheet"
	//	});
	//	
	//	this.constructsPanel.getTopToolbar().add(button);
	
	//	(function(){  
	//          Ext.get('loading').remove();  
	//          Ext.get('loading-mask').fadeOut({remove:true});  
	//        }).defer(250);
	
	//	Ext.Ajax.on('beforerequest', this.annealingLabel.show(), this);
	//	Ext.Ajax.on('requestcomplete', this.annealingLabel.hide(), this);
	//	Ext.Ajax.on('requestexception', this.annealingLabel.hide(), this);
	},
	
	//*******************************************************	
	//
	//	Event Handlers
	//
	//*******************************************************
	
	assembleButtonClickHandler: function(button, event) 
	{
		this.assemble();
	},
	
	emptyBinButtonClickHandler: function(button, event) 
	{
		var insertBinSelectModel = this.planGridPanel.getSelectionModel();
		var binCoordinates = insertBinSelectModel.getSelectedCell();
	
		if (binCoordinates !== null)
		{
			var binRow = binCoordinates[0];
			var binColumn = binCoordinates[1];
			var record = this.planGridPanel.getStore().getAt(binRow);
			var fieldName = this.planGridPanel.getColumnModel().getDataIndex(binColumn);
			record.data[fieldName] = "";
			record.commit();
			this.annealingResultTextArea.setValue('');
		}
		else
		{	
			Ext.Msg.alert('Empty Bin', 'Please select a bin to empty.');
		}
	},
	
	insertBinCellSelectHandler:function(selectModel, rowIndex, colIndex)
	{
		var record = this.planGridPanel.getStore().getAt(rowIndex);
		var fieldName = this.planGridPanel.getColumnModel().getDataIndex(colIndex);
		var insert = record.get(fieldName);
	
	
		if(insert.length > 0)
		{
			if(insert.search(/\//) > -1)
			{
				this.anneal(insert);
			}
	
			this.provideFeedback("Annealing the insert...");
		}
		else
		{
			this.annealingResultTextArea.setValue('');
		}
	},
	
	constructsGridRowSelectHandler: function ( selectModel, rowIndex, record )
	{
		//TODO Finish displaying annealing of fwd and rev sequences
	
		var id = record.get("identifier");
		var fwdSeq = record.get("fwdSeq");
		var revSeq = record.get("revSeq");
	
		this.annealConstruct("Construct " + id + " Fwd Strand", fwdSeq, "Construct " + id + " Rev Strand", revSeq)
	},
	
	annealInsertResultHandler:function(response, opts)
	{
		if(response !== null && response.responseText.length > 0)
		{	
			this.annealingResultTextArea.setValue(response.responseText);
			this.provideFeedback("Annealing completed.");
		}
		else
		{
			this.annealRequestErrorHandler(response);
		}
	},
	
	annealConstructResultHandler:function(response, opts)
	{
		if(response !== null && response.responseText.length > 0)
		{	
			this.constructTextArea.setValue(response.responseText);
		}
		else
		{
			this.annealRequestErrorHandler(response);
		}
	},
	
	annealRequestErrorHandler:function(response, opts)
	{
		this.provideFeedback('There was an error while attempting to anneal the sequences.\n' + 'Error: ' + response.responseText);
	},
	
	assembleRequestResultHandler:function(response, opts)
	{
		if(response !== null && response.responseText.length > 0)
		{	
			var constructsJSON = response.responseText;
			var constructs = Ext.util.JSON.decode(constructsJSON); 
	
			var store = this.constructsEditorGrid.getStore();
			store.loadData(constructs, false);
	
			this.centerTabPanel.activate("constructsPanel");
			this.provideFeedback('The Assembly was completed.');
		}
		else
		{
			this.assembleRequestErrorHandler(response);
		}
	},
	
	assembleRequestErrorHandler:function(response, opts)
	{
		Ext.Msg.alert('Assemble', 'There was an error while attempting to assemble the constructs.\n' + 'Error: ' + response.responseText);
	},
	
	constructsCSVButtonClickHandler:function(button, event)
	{
		var csvText = this.generateCSVText(this.constructsEditorGrid.getStore());
		var window = new TextViewerWindow();
		window.add({
			xtype: 'flash',
			url: './textviewer/TextViewer.swf',
			flashVars:{text:csvText}
		});
		window.show();
		window.center();
	},
	
	//exportConstructsButtonClickHandler:function(button, event)
	//{
	//	//var exportWindow = window.open("","Constructs","width=640,height=480,left=10,top=10"); 
	//	var exportWindow = window.open("","Constructs","width=640,height=480");
	////	exportWindow.document.write(
	////			"<table border=\"1\" bordercolor=\"#000000\" cellpadding=\"3\" cellspacing=\"0\" style=\"width:100%\">" +
	////					"<tbody>" +
	////					"<tr>"+
	////					"<th>Serial Number</th>" +
	////					"<th>Status</th>" +
	////					"<th>Description</th>" +
	////					"<th>Forward Sequence</th>"+
	////					"</tr>" +
	////					"<tr>" +
	////					"<td>0</td>" +
	////					"<td>Test</td>" +
	////					"<td>Test</td>" +
	////					"<td>Test</td>" +
	////					"</tr>" +
	////					"</tbody>" +
	////			"</table>");
	//	
	//	var table = exportWindow.document.createElement(HTMLTableElement.tagName);
	//	
	//	
	//	exportWindow.alert("Use File/Save As in the menu bar to save this document.");
	//},
	
	
	//*******************************************************	
	//
	//	Public Functions
	//
	//*******************************************************	
	
	placePartInBin: function(part) 
	{ 
		var insertBinSelectModel = this.planGridPanel.getSelectionModel();
		var binCoordinates = insertBinSelectModel.getSelectedCell();
		var planStore = this.planGridPanel.getStore();
	
		if (binCoordinates !== null)
		{
			var binRow = binCoordinates[0];
			var binColumn = binCoordinates[1];
			var record = planStore.getAt(binRow);
			var fieldName = this.planGridPanel.getColumnModel().getDataIndex(binColumn);
			var oldEntry = record.get(fieldName);
			var newEntry = this.generateBinEntry(oldEntry, part.id);
			record.data[fieldName] = newEntry;
			record.commit();
	//		planStore.commitChanges();
			this.addPart(part);
	
			if(this.shouldAnneal)
			{
				this.provideFeedback("Annealing the insert...");
				this.anneal(newEntry);
			}
		}
		else
		{
			Ext.Msg.alert('Assembler', 'Please select a bin to place the part.');
		}
	},
	
	generateBinEntry: function(oldBinEntry, newBinEntry) 
	{ 
		if(oldBinEntry.length === 0)
		{
			this.shouldAnneal = false;
			return newBinEntry;
		}
		else
		{
			if(oldBinEntry.search(/\//) === -1)
			{
				newBinEntry = oldBinEntry + " \/ " + newBinEntry;
				this.shouldAnneal = true;
				return newBinEntry;
			}
			else
			{
				this.shouldAnneal = false;
				return newBinEntry;
			}
		}
	},
	
	anneal: function(insert) 
	{ 
		if(insert.length > 0)
		{
			if(insert.search(/\//) > -1)
			{
				var binEntries = insert.split('/');
				var fwdPartID = binEntries[0].trim();
				var revPartID = binEntries[1].trim();
				var fwdPart = this.fetchPart(fwdPartID);
				var revPart = this.fetchPart(revPartID);
	
				Ext.Ajax.request({
					   url: this.annealerURL,
					   method: "POST",
					   success: this.annealInsertResultHandler,
					   failure: this.annealRequestErrorHandler,
					   params: {
							FwdSeqID: fwdPart.id,
							FwdSeq: fwdPart.data.sequence,
							RevSeqID: revPart.id,
							RevSeq: revPart.data.sequence
				        },
					   scope: this
				});
			}
		}
	},
	
	annealConstruct: function(fwdSeqID, fwdSeq, revSeqID, revSeq) 
	{ 
		Ext.Ajax.request({
			   url: this.annealerURL,
			   method: "POST",
			   success: this.annealConstructResultHandler,
			   failure: this.annealRequestErrorHandler,
			   params: {
					FwdSeqID: fwdSeqID,
					FwdSeq: fwdSeq,
					RevSeqID: revSeqID,
					RevSeq: revSeq
				},
			   scope: this
		});
	},
	
	fetchPart: function(partID)
	{
		for(var i = 0; i < this.partInstances.length; ++i)
		{
			if(this.partInstances[i].id === partID)
			{
				return this.partInstances[i];
			}
		}
	},
	
	addPart: function(part)
	{
		// Add code to guard against duplicates
	
		this.partInstances.push(part);
	},
	
	assemble: function() 
	{ 	
		var record = null;
		var rowCount = this.planGridPanel.store.getCount();
		var bins = [];
		var binContent = null;
		var columnName = null;
		var parts = [];
	
		this.planGridPanel.store.commitChanges();
	
		for(var i = 0; i < rowCount; i += 1)
		{
			record = this.planGridPanel.store.getAt(i);
			bins[i] = [];
			var columnCount = this.planGridPanel.getColumnModel().getColumnCount(false);
	
			for(var j = 0; j < columnCount; j += 1)
			{
				columnName = this.planGridPanel.getColumnModel().getDataIndex(j);
				binContent = record.get(columnName);
				bins[i].push(binContent);
			}
		}
	
		var partsCount = this.partInstances.length;
	
		for(var n = 0; n < partsCount; ++n)
		{
			parts.push([this.partInstances[n].id, this.partInstances[n].data.sequence ]);
		}
	
		var partsJSON = Ext.util.JSON.encode(parts);
		var binsJSON = Ext.util.JSON.encode(bins);
	
		Ext.Ajax.defaultHeaders = {
			    'Powered-By': 'Ext'
			};
	
		Ext.Ajax.request({
			   url: this.assemblerURL,
			   method: "POST",
			   success: this.assembleRequestResultHandler,
			   failure: this.assembleRequestErrorHandler,
			   params: {bins: binsJSON, parts: partsJSON},
			   scope: this
		});
	},
	
	generateCSVText:function(store)
	{
		var csvText = null;
		var record = null;
		var rowCount = store.getCount();
		var rows = [];
		var fields = null;
		var data = null;
	
		for(var i = 0; i < rowCount; i += 1)
		{
			record = store.getAt(i);
			fields = [];
			data = record.data;
			fields.push(data.identifier);
			fields.push(data.description);
			fields.push(data.status);
			fields.push(data.fwdSeq);
	
			rows.push(fields.join(","));
		}
	
		if(rows.length > 0)
		{
			csvText = rows.join("\n");
		}
		else
		{
			csvText = "";
		}
	
		return csvText;
	},
	
	provideFeedback: function(feedback)
	{
		var priorFeedback = this.feedbackTextArea.getValue();
		var newFeedback = priorFeedback + feedback + "\n";
		this.feedbackTextArea.setValue(newFeedback);
	}
});

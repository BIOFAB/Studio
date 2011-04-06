/*
 * 
 * File: StudioViewport.js
 *
 */

StudioViewport = Ext.extend(StudioViewportUi, {
//	refinerWindow: null,
//	designerWindow: null,
//	assemblerPanel: null,
//	checkerWindow: null,
	
    initComponent: function() 
    {
    	StudioViewport.superclass.initComponent.call(this);
        
//		var selectionModel = this.oligoGridPanel.getSelectionModel();
//		selectionModel.on('rowselect', this.gridRowSelectHandler, this);
//
//		var constructsGridSelectionModel = this.constructGridPanel.getSelectionModel();
//		constructsGridSelectionModel.on('rowselect', this.constructsGridSelectHandler, this);
    
//		this.refinerButton.setHandler(this.refinerButtonClickHandler, this);
//		this.seqDesignerButton.setHandler(this.designerButtonClickHandler, this);
//		this.assemblerButton.setHandler(this.assemblerButtonClickHandler, this);
                this.checkerButton.setHandler(this.checkerButtonClickHandler, this);
                this.westTabPanel.setActiveTab(this.constructGridPanel);
                this.checkerButtonClickHandler(null, null);
    },

	gridRowSelectHandler: function(selectionModel, rowIndex, row) 
	{ 
		if(this.assemblerPanel !== null)
		{
			this.assemblerPanel.placePartInBin(row);
		}
	},
	
	constructsGridSelectHandler: function(selectModel, rowIndex, record)
	{
	    var id = record.get("biofabID");
		var tab = this.infoTabPanel.add({
            title: id,
            itemId: id,
            id: id,
            iconCls: 'tabs',
            bodyStyle: 'padding:10px; word-wrap:break-word',
            closable: true
        });
		tab.add({
			xtype: 'flash',
			url: '../designviewer/DesignViewer.swf',
			flashVars:{
				sequence:record.get("sequence"),
				identifier:id
			}
		});
	    this.infoTabPanel.setActiveTab(tab);
	},
	    
//	refinerButtonClickHandler: function(button, event)
//	{
//		if(this.refinerWindow === null)
//		{
//			this.refinerWindow = new RefinerWindow();
//			this.refinerWindow.show();
//		}
//		else
//		{
//			this.refinerWindow.show();
//		}
//	},
	
//	designerButtonClickHandler: function(button, event)
//	{
//		var panel = new SeqDesignerPanel();
//
//		var tab = this.infoTabPanel.add(panel);
//
//	    this.infoTabPanel.setActiveTab(tab);
//	},
	
//	designerButtonClickHandler: function(button, event)
//	{
//		if(this.designerWindow === null)
//		{
//			this.designerWindow = new SequenceDesignerWindow();
//			this.designerWindow.show();
//		}
//		else
//		{
//			this.designerWindow.show();
//		}
//	},
	
//	assemblerButtonClickHandler: function(button, event)
//	{
//		this.assemblerPanel = new AssemblerPanel();
//		var tab = this.infoTabPanel.add(this.assemblerPanel);
//	    this.infoTabPanel.setActiveTab(tab);
//	},
	
//	assemblerButtonClickHandler: function(button, event)
//	{
//		if(this.assemblerWindow === null)
//		{
//			this.assemblerWindow = new AssemblerWindow();
//			this.assemblerWindow.show();
//		}
//		else
//		{
//			this.assemblerWindow.show();
//		}
//	},
	
	checkerButtonClickHandler: function(button, event)
	{
            var panel = new SeqCheckerPanel();
            var tab = this.infoTabPanel.add(panel);
            this.infoTabPanel.setActiveTab(tab);
	}

//	rbsCalcButtonClickHandler: function(button, event)
//	{
//      //		var panel = new RbsCalcPanel();
//    //    panel.add(rbs_calculate_form);
//          var panel = RbsCalcPanel;
//            var tab = this.infoTabPanel.add(panel);
//	  this.infoTabPanel.setActiveTab(tab);
//	},

	
//	checkerButtonClickHandler: function(button, event)
//	{
//		if(this.checkerWindow === null)
//		{
//			this.checkerWindow = new SequenceCheckerWindow();
//			this.checkerWindow.show();
//		}
//		else
//		{
//			this.checkerWindow.show();
//		}
//	},
	
//	underDevelopmentHandler: function(button, event)
//	{
//	    Ext.Msg.alert('BIOFAB Studio', 'Under development...');
//	}
});

/*
 *
 *
 *
 */

Ext.define('PlasmidViewer', {
    extend: 'Ext.panel.Panel',
    title: 'Plasmid',
    layout: 'fit',
    tpl: '',
    closable: true,
    autoScroll: false,

    //Subcomponents
    mainTabPanel: null,
    designPanel: null,
    plasmidDesignPanel: null,
    plasmidDesignExportButton: null,
    plasmidDesignPanelText: null,
    
    //Data Members
    plasmidRecord: null,
    plasmidId: null,

    //Function Members
    constructor: function() {
        this.items = [
            {
                xtype: 'tabpanel',
                itemId: 'mainTabPanel',
                activeTab: 0,
                items:[
                    {
                        xtype: 'panel',
                        itemId: 'designPanel',
                        title: 'Design',
                        layout: 'border',
                        items: [
                            {
                                xtype: 'panel',
                                itemId: 'plasmidDesignPanel',
                                region: 'center',
                                layout: 'fit',
                                split: true,
                                tbar: {
                                    xtype: 'toolbar',
                                    itemId: 'plasmidDesignPanelToolbar',
                                    items: [
                                        {
                                            xtype: 'tbtext',
                                            itemId: 'plasmidDesignPanelText',
                                            text: 'Fetching Design...',
                                            hidden: true
                                        },
                                        {
                                            xtype: 'tbfill'
                                        },
                                        {
                                            xtype: 'button',
                                            itemId: 'plasmidDesignExportButton',
                                            text: 'Export',
                                            tooltip: 'Export the plasmid design in Genbank format.'
                                        }
                                    ]
                                },
                                items:[]
                            }
                        ]
                    }
                ]
             
            }
        ];
        
        this.callParent();
        
        this.mainTabPanel = this.getComponent('mainTabPanel');
        this.designPanel = this.mainTabPanel.getComponent('designPanel');
        this.plasmidDesignPanel = this.designPanel.getComponent('plasmidDesignPanel');
        this.plasmidDesignExportButton = this.plasmidDesignPanel.getComponent('plasmidDesignPanelToolbar').getComponent('plasmidDesignExportButton');
        this.plasmidDesignPanelText = this.plasmidDesignPanel.getComponent('plasmidDesignPanelToolbar').getComponent('plasmidDesignPanelText');
        this.plasmidDesignExportButton.setHandler(this.plasmidDesignExportButtonHandler, this);
 
    },
    
    displayInfo: function(plasmidRecord)
    {
        this.plasmidRecord = plasmidRecord;
        this.plasmidId = this.plasmidRecord.get('biofabId');
        this.setTitle(this.plasmidId);

        //TODO Deal with null plasmidId
        this.fetchPlasmidDesign(this.plasmidId);
    },
    
    fetchPlasmidDesign:function(plasmidID)
    {
        this.plasmidDesignPanelText.setVisible(true);
        Ext.Ajax.request({
                   url: './plasmids',
                   method: "GET",
                   success: this.fetchPlasmidDesignResultHandler,
                   failure: this.fetchPlasmidDesignErrorHandler,
                   params: {
                                id: plasmidID,
                                format: 'insd'
                            },
                   scope: this
        });
    },
    
    //******************
    //
    //  Event Handlers
    //
    //******************
    
    fetchPlasmidDesignResultHandler: function(response, opts)
    {
        this.plasmidDesignPanelText.setVisible(false);
        var flash = {
                xtype: 'flash',
                url:'designviewer/DesignViewer.swf',
                flashVars:{design:response.responseText}
            };
        this.plasmidDesignPanel.add(flash);
        //this.plasmidDesignPanel.doLayout();
        this.mainTabPanel.setActiveTab(0);
    },

    fetchPlasmidDesignErrorHandler: function(response, opts)
    {
       this.plasmidDesignPanelText.setVisible(false);
       Ext.Msg.alert('Fetch Design', 'There was an error while attempting to fetch the design.\n' + 'Error: ' + response.responseText);
    },
    
    plasmidDesignExportButtonHandler: function()
    {
        var genbankWindow = window.open('./plasmids?id=' + this.plasmidId + '&format=genbank','Genbank File for ' + this.plasmidId,'width=640,height=480');
        genbankWindow.alert("Use File/Save As in the menu bar to save this document.");
        genbankWindow.scrollbars.visible = true;
    }
});

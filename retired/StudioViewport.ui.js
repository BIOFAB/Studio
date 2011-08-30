/*
 *
 * File: StudioViewport.ui.js
 *
 *
 */

StudioViewportUi = Ext.extend(Ext.Viewport, {
    layout: 'border',
    id: 'studioViewport',
    initComponent: function() {
        Ext.define('Plasmid', {
            extend: 'Ext.data.Model',
            fields: [
                {name: 'id', type: 'int'},
                {name: 'biofab_id',  type: 'string'},
                {name: 'description', type: 'string'}
            ]
        });

       var plasmidStore = new Ext.data.Store({
           model: 'Plasmid',
           proxy: {
            type: 'ajax',
            url : PLASMIDS_URL,
            reader: 'json'
           },
           autoLoad: true
       });

        this.items = [
            {
                xtype: 'tabpanel',
                activeTab: 0,
                region: 'center',
                split: true,
                id: 'centerTabPanel',
                items:[]
            },
            {
                xtype: 'panel',
                region: 'north',
                layout: 'fit',
                height: 30,
                id: 'northPanel',
                items: [
                    {
                        xtype: 'toolbar',
                        id: 'mainToolbar',
                        items: [
                            {
                                xtype: 'button',
                                text: 'RNA Folder',
                                id: 'rnaFolderButton'
                            },
                            {
                                xtype: 'tbseparator'
                            },
                            {
                                xtype: 'button',
                                text: 'Device Editor',
                                id: 'deviceEditorButton',
                                disabled: false
                            },
                            {
                                xtype: 'tbseparator'
                            },
                            {
                                xtype: 'button',
                                text: 'Sequence Checker',
                                id: 'checkerButton'
                            }
                        ]
                    }
                ]
            },
            {
                xtype: 'tabpanel',
                activeTab: 0,
                width: 400,
                style: '',
                collapsible: true,
                region: 'west',
                split: true,
                id: 'westTabPanel',
                //ref: 'westTabPanel',
                items: [
                    {
                        xtype: 'grid',
                        title: 'Plasmids',
                        store: plasmidStore,
                        stripeRows: true,
                        columnLines: true,
                        //ref: '../plasmidsGridPanel',
                        id: 'plasmidsGridPanel',
//                        selModel: new Ext.grid.RowSelectionModel({
//                        singleSelect: true
//                        }),
                        columns: [
                            {
                                xtype: 'gridcolumn',
                                dataIndex: 'biofab_id',
                                header: 'Identifier',
                                sortable: true,
                                width: 100
                                //editable: false
                            },
                            {
                                xtype: 'gridcolumn',
                                header: 'Description',
                                sortable: true,
                                width: 300,
                                //editable: false,
                                dataIndex: 'description'
                            }
                        ]
                    }
                ]
            }
        ];
        StudioViewportUi.superclass.initComponent.call(this);
    }
});

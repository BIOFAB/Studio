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
        this.items = [
            {
                xtype: 'tabpanel',
                activeTab: 2,
                region: 'center',
                split: true,
                ref: 'infoTabPanel',
                id: 'infoTabPanel'
            },
            {
                xtype: 'panel',
                region: 'north',
                layout: 'vbox',
                height: 30,
                id: 'northPanel',
                items: [
                    {
                        xtype: 'toolbar',
                        //height: 78,
                        ref: '../toolbar',
                        id: 'mainToolbar',
                        items: [
                            {
                                xtype: 'button',
                                text: 'Checker',
                                ref: '../../checkerButton',
                                id: 'checkerButton'
                            }
                        ]
                    }
                ]
            },
            {
                xtype: 'tabpanel',
                activeTab: 3,
                width: 400,
                style: '',
                collapsible: true,
                region: 'west',
                split: true,
                id: 'westTabPanel',
                ref: 'westTabPanel',
                items: [
                    {
                        xtype: 'grid',
                        title: 'Constructs',
                        store: 'constructStore',
                        stripeRows: true,
                        columnLines: true,
                        ref: '../constructGridPanel',
                        id: 'constructGridPanel',
                        selModel: new Ext.grid.RowSelectionModel({
                        singleSelect: true
                        }),
                        columns: [
                            {
                                xtype: 'gridcolumn',
                                dataIndex: 'id',
                                header: 'Identifier',
                                sortable: true,
                                width: 100,
                                editable: false
                            },
                            {
                                xtype: 'gridcolumn',
                                header: 'Description',
                                sortable: true,
                                width: 300,
                                editable: false,
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

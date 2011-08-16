Ext.define('Plasmid', {
    extend: 'Ext.data.Model',
    fields: [
        {name: 'index', type: 'int'},
        {name: 'biofabId',  type: 'string'},
        {name: 'description', type: 'string'}
    ]
});

Ext.define('Oligo', {
    extend: 'Ext.data.Model',
    fields: [
        {name: 'index', type: 'int'},
        {name: 'biofabId',  type: 'string'},
        {name: 'description', type: 'string'},
        {name: 'dnaSequence', type: 'string'}
    ]
});

Ext.define('Feature', {
    extend: 'Ext.data.Model',
    fields: [
        {name: 'index', type: 'int'},
        {name: 'biofabId',  type: 'string'},
        {name: 'genbankType',  type: 'string'},
        {name: 'biofabType',  type: 'string'},
        {name: 'description', type: 'string'},
        {name: 'dnaSequence', type: 'string'}
    ]
});
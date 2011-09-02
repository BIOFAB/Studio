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

Ext.define('LocalFile', {
    extend: 'Ext.data.Model',
    fields: [
        {name: 'name', type: 'string'},
        {name: 'size',  type: 'int'}
    ]
});

Ext.define('FileNameToken', {
    extend: 'Ext.data.Model',
    fields: [
        {name: 'position', type: 'int'},
        {name: 'token',  type: 'string'},
        {name: 'type',  type: 'string'}
    ]
});
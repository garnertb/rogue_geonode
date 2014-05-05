/*
 * requires ../GeoGit.js and History.js
 */
var GeoGitService = (function(){
	var repo;

	return {
		init: function(options){
            this.getStats();
		},

        getGeoGitEndpoint:function(){
            return GeoGit.url + 'geogit/' + GeoGit.workspace + ':' + GeoGit.store;
        },

        getTestData:function(){
            return {"response":{"success":true,"Statistics":{"latestCommit":{"id":"f1a74f39eb4fbd6befeac7bf5e3ba4857d7289d7","tree":"8eff849dfff76707c5131dd12815cbb6eb6456dc","parents":{"id":"030e9ed023567099698b21e176fb26b9cd750d72"},"author":{"name":"sclark","email":"","timestamp":1392837789253,"timeZoneOffset":0},"committer":{"name":"","email":"","timestamp":1392837789253,"timeZoneOffset":0},"message":"Reverted changes made to centros_medicos\/fid--1658f1ca_143fe6781fa_-7ffd. Applied via MapLoom."},"firstCommit":{"id":"0c2e22effd3967128bc4fc0740a64e436c1b1fc0","tree":"92b39b23d70ea38ccb09e2981be6470ab6100647","parents":"","author":{"name":"rogue","email":"rogue@lmnsolutions.com","timestamp":1378414983737,"timeZoneOffset":-25200000},"committer":{"name":"rogue","email":"rogue@lmnsolutions.com","timestamp":1378414983737,"timeZoneOffset":-25200000},"message":"importacion inicial"},"totalCommits":7,"Authors":{"Author":[{"name":"sclark"},{"name":"bobby","email":"bobby@bob.com"},{"name":"web8","email":"web8@lmnsolutions.com"},{"name":"rogue","email":"rogue@lmnsolutions.com"}],"totalAuthors":4}}}}
        },

        getStats: function(){
            if(GeoGit.url && GeoGit.workspace && GeoGit.store && GeoGit.layername){
                var request = GeoGit.url + "rest/workspaces/" + GeoGit.workspace + "/datastores/" + GeoGit.store +
                    "/featuretypes/" + GeoGit.layername + ".json";
                console.log(request);
            }
        }
	}
})();

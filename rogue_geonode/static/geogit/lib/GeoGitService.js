/*
 * requires ../GeoGit.js and History.js
 */
var GeoGitService = (function(){
	var repo;

	return {
		init: function(options){
            this.getStats();
            console.log(this.getGeoGitEndpoint());
		},

        getGeoGitEndpoint:function(){
            return GeoGit.url + 'geogit/' + GeoGit.workspace + ':' + GeoGit.store
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

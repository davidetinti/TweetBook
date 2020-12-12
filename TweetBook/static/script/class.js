class MapParameters {
    constructor() {
        this.lat = 44.456348;
        this.lng = 11.574575;
        this.zoom = 4;
        this.poi = [];
        this.heat_markers = [];
    }
}

class SearchParameters {
    constructor() {
        this.keywords = "";
        this.retweets = false;
        this.replies = false;
        this.only_geolocated = false;
        this.stream = false;
        this.user = "";
        this.location = "";
        this.hashtag = "";
        this.tag = "";
        this.share = {
            active: false,
            hours: 0,
            mins: 0,
            interval: null,
        };
        this.mail = {
            active: false,
            hours: 0,
            mins: 0,
            interval: null,
        };
        this.last_mail_id = null;
    }
}

class Section {
    constructor(name, popover_name, icon) {
        this.name = name;
        this.popover_name = popover_name;
        this.icon = icon;
    }
}

class Page {
    constructor() {
        this.id = Date.now();
        this.name = "";
        this.active_section = 0;
        this.search_parameters = new SearchParameters();
        this.maps = new MapParameters();
        this.tweets = [];
        this.is_map_initialized = false;
        this.selected_geo_tweets = [];
        this.graphs = {};
    }
}

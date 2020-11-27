/* Determina se saranno utilizzate
le API 1.1 (true) o 2.0 (false)
Nel codice sono inseriti diversi if che mutano
le funzioni per adattarle alla API utilizzate
e ai diversi oggetti che ritornano */
const api1 = true;

// Close websocket when webpage closes
window.addEventListener("unload", function(event) {
    if (vm.socket) vm.socket.close();
});

class Page {
    constructor() {
        this.id = Date.now();
        this.name = "";
        this.tweets = [];
        if (!api1) {
            this.includes = null;
            this.meta = null;
            this.matching_rules = null;
        }
        this.search_parameters = {
            keywords: "",
            retweets: false,
            replies: false,
            stream: false,
            user: "",
            location: "",
            hashtag: "",
            tag: "",
        };
        this.selected_section = 0;
        this.maps = {
            lat: 44.456348,
            lng: 11.574575,
            zoom: 4,
            poi: [],
            heat_markers: [],
        };
        this.selected_tweets = [];
        this.selected_geo_tweets = [];
        this.graphs = {};
    }

    initSearch() {
        this.maps.poi.forEach(poi => {
            vm.removeMarkers(null, poi);
        });
        this.tweets = [];
        if (!api1) {
            this.includes = null;
            this.meta = null;
        }
        this.maps = {
            lat: 44.456348,
            lng: 11.574575,
            zoom: 4,
            poi: [],
            heat_markers: [],
        };
        this.selected_tweets = []
        this.selected_geo_tweets = [];
        this.graphs = {};
    }
}

class Section {
    constructor(name, icon) {
        this.name = name;
        this.icon = icon;
    }
}

var vm = new Vue({
    delimiters: ["${", "}"],
    el: "#app",
    data: {
        oldapi: api1, // estensione di api1 per utilizzare la variabile in HTML
        sections: [
            new Section("Cerca", "fa-search"),
            new Section("Mappa", "fa-map-marker-alt"),
            new Section("Grafico a barre", "fa-chart-bar"),
            new Section("Grafico a torta", "fa-chart-pie"),
        ],
        pages: [new Page()],
        active_page: null,
        loadedFiles: [],
        map: null,
        layer: null,
        socket: null,
        stream_connection_open: false,
        changing_stream_query: false
    },
    computed: {
        section_content_class: function () {
            return {
                'flex-column': this.active_section.name == 'Cerca',
                'flex-row': this.active_section.name == 'Mappa'
            }
        },
        geolocalized_tweet: function () {
            let array = [];
            if (this.oldapi) {
                this.active_page.tweets.forEach((tweet) => {
                    if (tweet.place) array.push(tweet);     
                })
            } else {
                // implementazione mancante per le API 2.0
            }
            return array;
        },
        /* Media della ricerca attuale */
        current_page_media: function () {
            let array = [];
            if (this.oldapi) {
                this.active_page.tweets.forEach((tweet) => {
                    if (tweet.extended_entities) {
                        tweet.extended_entities.media.forEach((media) => {
                            array = array.concat({
                                url: media.media_url,
                                tweet_id: tweet.id_str,
                            })
                        })
                    }
                })
            } else {
                if (this.active_page.includes && this.active_page.includes.media) {
                    this.active_page.includes.media.forEach((media) => {
                        array = array.concat({
                            url: media.url ? media.url : media.preview_image_url,
                            /* Funzione chiamata quando si clicca su di una immagine,
            scorre iterativamente tutti i media di tutti i tweet per
            risalire all'id (un po brutta ma era l'unico modo) */
                            tweet_id: function () {
                                for (let i = 0; i < vm.$data.active_page.tweets.length; i++) {
                                    let tweet = vm.$data.active_page.tweets[i];
                                    if (tweet.attachments) {
                                        if (tweet.attachments.media_keys) {
                                            let media_keys = tweet.attachments.media_keys;
                                            for (let j = 0; j < media_keys.length; j++) {
                                                if (media_keys[j] == media.media_key) {
                                                    return tweet.id;
                                                }
                                            }
                                        }
                                    }
                                }
                                return undefined;
                            },
                        });
                    });
                }
            }
            return array;
        },
        active_section: function () {
            return this.sections[this.active_page.selected_section];
        },
        map_dimension: function () {
            return {
                height: this.active_section.name == "Mappa" ? "100%" : "0%",
                width: this.active_section.name == "Mappa" ? "calc(100% - 200px)" : "0%",
            };
        },
        page_selected_tweets: function () {
            return this.active_page.selected_tweets;
        },
    },
    methods: {
        toggleSelection(object, array) {
            if (array.indexOf(object) != -1) {
                array.splice(array.indexOf(object), 1)
                this.removeMarkers(null, this.creationMarkerMap(object, false));
            } else {
                array.push(object);
                this.creationMarkerMap(object, true);
            }
        },
        selectAll() {
            this.deselectAll();
            this.active_page.selected_geo_tweets = this.geolocalized_tweet.slice();
            this.active_page.selected_geo_tweets.forEach(tweet => {
                this.creationMarkerMap(tweet, true);
            });
        },
        deselectAll() {
            while (this.active_page.maps.poi.length > 0) {
                this.removeMarkers(null, this.active_page.maps.poi[0]);
            }
            this.active_page.selected_geo_tweets = []
        },
        /* Cerca in un array di oggetti il primo oggetto
        che ha la proprietà "fieldname" pari a "value" */
        connectData(fieldname, value, array) {
            return true; // TODO non funziona per streaming, devo sistemare (riccio)
            for (let i = 0; i < array.length; i++) {
                if (array[i][fieldname] == value) return array[i];
            }
        },
        /* Aggiunge la pagina passata come paramentro,
        se presente, altrimenti una vuota */
        addPage(page) {
            this.removeMarkers(this.active_page, null);
            this.pages.push(page ? page : new Page());
            this.active_page = this.pages[this.pages.length - 1];
            this.reloadMarkers(page ? page : this.active_page, null);
            this.reloadHeatMap();
        },
        /* Imposta la pagina corrente e riposiziona la mappa
        sulla sua ultima posizione in quella pagina */
        setActivePage(page) {
            this.removeMarkers(this.active_page, null);
            this.active_page = page;
            this.setMapLocation(page.maps.lat, page.maps.lng, page.maps.zoom);
            this.reloadHeatMap();
            this.reloadMarkers(page);
        },
        /* Imposta l'indice della sezione */
        setActiveSection(section_index) {
            this.active_page.selected_section = section_index;
        },
        /* Cambia la posizione puntata dalla mappa */
        setMapLocation(lat, lng, zoom) {
            if (this.map) {
                this.map.setCenter({
                    lat: lat,
                    lng: lng,
                });
                this.map.setZoom(zoom);
            }
        },
        /* Mostra la finestra di ricerca avanzata */
        showAdvancedSearchPopover() {
            this.$refs.popover.$emit("open");
        },
        /* Avvia la ricerca dei tweet tramite i parametri */
        search() {
            this.active_page.initSearch();
            let params = this.active_page.search_parameters;
            this.active_page.name = params.keywords;
            if (params.stream) {
                this.oldapi = false;
                this.streamTweets(params.keywords);
                return;
            }
            this.oldapi = true;
            fetch(
                "search/?keywords=" +
                params.keywords +
                "&retweets=" +
                params.retweets +
                "&replies=" +
                params.replies +
                "&user=" +
                params.user +
                "&location=" +
                params.location +
                "&hashtag=" +
                params.hashtag +
                "&tag=" +
                params.tag
            )
                .then((response) => response.json())
                .then((data) => {
                    if (this.oldapi) {
                        this.active_page.tweets = data.statuses;
                        this.creationHeatMap();
                        this.reloadHeatMap();
                    } else {
                        this.active_page.tweets = data.data;
                        this.active_page.includes = data.includes;
                        this.active_page.meta = data.meta;
                    }
                    /* DEBUG */
                    console.log("Data:");
                    console.log(data);
                });
        },
        streamTweets(keywords) {
            this.active_page.tweets = [];
            this.active_page.matching_rules = [];
            this.active_page.includes = [];

            params = this.active_page.search_parameters;
            keywords = keywords
                        + (params.retweets        ? " " : " -is:retweet")
                        + (params.replies         ? " " : " -is:reply")
                        + ((params.user == "")    ? " " : " from:" + params.user)
                        + ((params.hashtag == "") ? " " : " #" + params.hashtag)
                        + ((params.tag == "")     ? " " : " @" + params.tag)
            console.log('Search keywords: ' + keywords);

            // Send keywords into websocket connection
            if (!this.stream_connection_open) {
                this.stream_connection_open = true;
                this.socket = new WebSocket('ws://localhost');
                this.socket.onopen = () => this.socket.send(keywords);
            }
            else {
                this.socket.send(keywords);
                this.changing_stream_query = true;
            }
            // Update page on tweet received from streaming
            this.socket.addEventListener("message", function (event) {
                /*console.log('nuovo tweet con: ', JSON.parse(event.data).matching_rules[0].id) // TODO per fermare la visualizzazione dello stream appena cambio la query dello streaming, fino a che non arriva qualcosa secondo le nuove regole
                if (vm.changing_stream_query) {
                    console.log('sto cambiando');
                    var x = JSON.parse(JSON.stringify(vm.active_page.matching_rules));
                    console.log('vecchio: ', x, x[0]);
                    if (JSON.parse(event.data).matching_rules[0].id == x[0]){ 
                        console.log('non va bene, new/old: ', JSON.parse(event.data).matching_rules[0].id, vm.active_page.matching_rules[0]);
                        return;
                    }
                    else {
                        vm.changing_stream_query = false;
                        console.log('va bene, new/old: ', JSON.parse(event.data).matching_rules[0].id, vm.active_page.matching_rules[0]);
                    }
                } else {*/
                    if (!vm.active_page.search_parameters.stream)
                        return;
                    let tweet = JSON.parse(event.data);
                    vm.active_page.tweets.unshift(tweet.data);
                    vm.active_page.includes.unshift(tweet.includes);
                    vm.active_page.matching_rules.unshift(tweet.matching_rules[0].id);

                    if (vm.active_page.tweets.length > 100) {
                        vm.active_page.tweets.pop();
                        vm.active_page.includes.pop();
                        vm.active_page.matching_rules.pop();
                    }

                //}
            });          
        },
        /* Rimuove la pagina "page" dalla lista delle pagine */
        removePage(page) {
            if (this.pages.length > 1) {
                let index = this.pages.indexOf(page);
                this.removeMarkers(page, null);
                page.maps.poi = [];
                this.pages.splice(index, 1);
                if (page == this.active_page) {
                    if (index == this.pages.length)
                        this.active_page = this.pages[index - 1];
                    else this.active_page = this.pages[index];
                }
            }
        },
        /* Mostra nel pannello il tweet corrispondente a "tweet_id" */
        showTweet(tweet_id) {
            let tweet_wrapper = document.getElementById("tweet-lookup");
            if (tweet_wrapper && tweet_id) {
                /* Clear the tweet lookup panel */
                while (tweet_wrapper.hasChildNodes()) {
                    tweet_wrapper.removeChild(tweet_wrapper.lastChild);
                }
                /* Create the spinner for the tweet lookup panel */
                let opts = {
                    lines: 12, // The number of lines to draw
                    length: 38, // The length of each line
                    width: 17, // The line thickness
                    radius: 45, // The radius of the inner circle
                    scale: 0.4, // Scales overall size of the spinner
                    corners: 1, // Corner roundness (0..1)
                    speed: 1, // Rounds per second
                    rotate: 0, // The rotation offset
                    animation: "spinner-line-fade-quick", // The CSS animation name for the lines
                    direction: 1, // 1: clockwise, -1: counterclockwise
                    color: "#ffffff", // CSS color or array of colors
                    fadeColor: "transparent", // CSS color or array of colors
                    top: "50%", // Top position relative to parent
                    left: "0%", // Left position relative to parent
                    shadow: "0 0 1px transparent", // Box-shadow for the lines
                    className: "spinner", // The CSS class to assign to the spinner
                    position: "relative", // Element positioning
                };
                new Spin.Spinner(opts).spin(tweet_wrapper);
                /* Start the lookup */
                twttr.widgets
                    .createTweet(tweet_id, tweet_wrapper, {
                        theme: "dark",
                        lang: "it",
                    })
                    .then(() => {
                        tweet_wrapper.removeChild(tweet_wrapper.firstChild);
                        tweet_wrapper.firstChild.style["display"] = "block";
                    });
            }
        },
        /* Scarica un file JSON della pagina corrente */
        saveSearch() {
            if (this.active_page.tweets.length) {
                let data = JSON.stringify(this.active_page);
                let blob = new Blob([data], {
                    type: "application/json",
                });
                let filename = this.active_page.name;
                let link = document.createElement("a");
                link.download = filename;
                //Funzione createObjectURL cross-browser
                let createObjectURL =
                    (window.URL || window.webkitURL || {}).createObjectURL ||
                    function () { };
                link.href = createObjectURL(blob);
                link.click();
            }
        },
        /* Avvia l'importazione di un file */
        openFileSelector() {
            document.getElementById("upload-form-file").click();
        },
        /* Aggiunge una nuova pagina contenente i dati del file
        al percorso "file" */
        loadSearch(file) {
            if (file) {
                let path = file;
                let fileReader = new FileReader();
                let _this = this;
                fileReader.onload = function (event) {
                    try {
                        let text = event.target.result;
                        let json = JSON.parse(text);
                        if (_this.jsonFileErrors(json)) {
                            throw "jsonschemeerror";
                        }
                        _this.addPage(json);
                        _this.setActivePage(json);
                        _this.active_page.tweets.forEach((tweet) => {
                            _this.active_page.selected_tweets.push(tweet);
                        });
                        //se non è ancora stata fatta una ricerca rimuovo la pagina vuota
                        if (_this.pages[0].tweets.length == 0)
                            _this.removePage(_this.pages[0]);
                    } catch (err) {
                        if (err == "jsonschemeerror")
                            window.alert("file .json non contenente tweet");
                        else window.alert("Il file deve essere di tipo JSON!");
                    }
                };
                fileReader.readAsText(path, "utf-8");
            } else {
                window.alert("Inserire un file da caricare");
            }
        },
        /* Funzione che va a controllare l'integrità dell'oggetto page */
        jsonFileErrors(json) {
            if (!json.hasOwnProperty("name")) return true;
            if (!json.hasOwnProperty("tweets")) return true;
            if (!json.hasOwnProperty("search_parameters")) return true;
            //if (!json.hasOwnProperty('selected_images')) return true;
            return false;
        },
        /* Inizializza una mappa all'interno dell'elemento "element */
        initMap(element) {
            let center = {
                lat: 44.456348,
                lng: 11.574575
            };

            let map = new google.maps.Map(element, {
                zoom: 4,
                center: center,
                fullscreenControl: false,
                streetViewControl: false,
                mapTypeId: "satellite",
            });
            map.addListener("center_changed", () => {
                vm.$data.active_page.maps.lat = vm.map.center.lat();
                vm.$data.active_page.maps.lng = vm.map.center.lng();
            });
            map.addListener("zoom_changed", () => {
                vm.$data.active_page.maps.zoom = vm.map.zoom;
            });
            return map;
        },
        /* Crea heatmap */
        creationHeatMap() {
            var page = this.active_page.maps;
            page.heat_markers.splice(0, page.heat_markers.length);
            for (let tweet of this.active_page.tweets) {
                if (tweet.place != null) {
                    let lat =
                        tweet.place.bounding_box.coordinates[0][1][1] +
                        tweet.place.bounding_box.coordinates[0][0][1] +
                        tweet.place.bounding_box.coordinates[0][2][1] +
                        tweet.place.bounding_box.coordinates[0][3][1];
                    let long =
                        tweet.place.bounding_box.coordinates[0][1][0] +
                        tweet.place.bounding_box.coordinates[0][0][0] +
                        tweet.place.bounding_box.coordinates[0][2][0] +
                        tweet.place.bounding_box.coordinates[0][3][0];
                    lat = lat / 4;
                    long = long / 4;
                    page.heat_markers.push(new google.maps.LatLng(lat, long));
                }
            }
        },
        reloadHeatMap() {
            if (this.layer != null) this.layer.setMap(null);
            // Reload the map with the new heatmap PoI
            this.layer = new google.maps.visualization.HeatmapLayer({
                data: this.active_page.maps.heat_markers,
            });
            this.layer.setMap(this.map);
        },
        creationMarkerMap(tweet, insert_into_array) {
            var newpoi = null;
            var result = null;
            if (tweet.place != null) {
                let lat =
                    tweet.place.bounding_box.coordinates[0][1][1] +
                    tweet.place.bounding_box.coordinates[0][0][1] +
                    tweet.place.bounding_box.coordinates[0][2][1] +
                    tweet.place.bounding_box.coordinates[0][3][1];
                let long =
                    tweet.place.bounding_box.coordinates[0][1][0] +
                    tweet.place.bounding_box.coordinates[0][0][0] +
                    tweet.place.bounding_box.coordinates[0][2][0] +
                    tweet.place.bounding_box.coordinates[0][3][0];
                lat = lat / 4;
                long = long / 4;
                //Creazione POI
                //Marker
                let newmarker = new google.maps.Marker({
                    position: new google.maps.LatLng(lat, long),
                })
                //infowindow
                const contentInfoWindow = 
                '<div class="d-flex flex-column"  id="content">' +
                "<div>"+ "<strong>" + tweet.user.name+ "</strong>" + "</div>" +
                "<div>"+ tweet.text + "</div>" +
                ( typeof tweet.extended_entities !== "undefined" ? "<img height='auto' width='220' src='" + tweet.extended_entities.media[0].media_url + "'>" : "") +
                "</div>";
                let newinfowindow = new google.maps.InfoWindow({
                    content: contentInfoWindow,
                    maxWidth: 250,
                });
                newmarker.addListener("click", () => {
                    newinfowindow.open(this.map, newmarker);
                })
                //POI
                newpoi = {
                    marker: newmarker,
                    infowindow: newinfowindow,
                };
                this.active_page.maps.poi.push(newpoi);
                if (insert_into_array == true) {
                    newpoi.marker.setMap(this.map);
                    newpoi.infowindow.open(this.map, newpoi.marker);
                    result = this.active_page.maps.poi[this.active_page.maps.poi.length - 1];
                } else {
                    if (this.active_page.maps.poi.length > 0)
                        result = this.active_page.maps.poi.pop();
                }
            }
            return result;
        },
        reloadMarkers(page) {
            //Riscrivo i marker non eliminati nella mappa
            for (poi of page.maps.poi) {
                poi.infowindow.open(this.map, poi.marker);
                poi.marker.setMap(this.map);
            }
        },
        removeMarkers(page, element) {
            //Primo caso: nascondo tutti i marker di quella pagina.
            if (page != null && element == null) {
                for (let poi of page.maps.poi) {
                    poi.infowindow.close();
                    poi.marker.setMap(null);
                }
            }
            //Secondo caso: rimuovo completamente un marker
            else if (page == null && element != null) {
                let indice = -1;
                for (let i = 0; i < this.active_page.maps.poi.length; i++) {
                    if (element.infowindow.content === this.active_page.maps.poi[i].infowindow.content)
                        indice = i;
                }
                if (indice != -1) {
                    this.active_page.maps.poi[indice].infowindow.close();
                    this.active_page.maps.poi[indice].marker.setMap(null);
                    this.active_page.maps.poi.splice(indice, 1);
                }
            } else
                console.error("Remove error!");
        },
    },
    watch: {
        /* Carica il file al momento della selezione */
        loadedFiles: function (thisFile) {
            for (let i = 0; i < thisFile.length; i++) {
                this.loadSearch(thisFile[i]);
            }
        },
    },
    created: function () {
        this.active_page = this.pages[0];
        this.setActiveSection(0);
    },
});

window.onload = function () {
    /* Abilita la ricerca con la pressione del tasto invio */
    let input = document.getElementById("search-input-id");
    input.addEventListener("keyup", function (event) {
        if (event.keyCode === 13 || event.key === 13) {
            event.preventDefault();
            document.getElementById("search-button-id").click();
        }
    });

    /* Inizializza la mappa */
    vm.$data.map = vm.initMap(document.getElementById("map"));
};

/* Rende la bottom page-bar scrollabile */
document.addEventListener("DOMContentLoaded", function () {
    let ele = document.getElementsByClassName("pages-wrapper")[0];
    ele.style.cursor = "grab";

    let pos = {
        top: 0,
        left: 0,
        x: 0,
        y: 0
    };

    let mouseDownHandler = function (e) {
        ele.style.cursor = "grabbing";
        ele.style.userSelect = "none";

        pos = {
            left: ele.scrollLeft,
            top: ele.scrollTop,
            // Get the current mouse position
            x: e.clientX,
            y: e.clientY,
        };

        document.addEventListener("mousemove", mouseMoveHandler);
        document.addEventListener("mouseup", mouseUpHandler);
    };

    let mouseMoveHandler = function (e) {
        // How far the mouse has been moved
        let dx = e.clientX - pos.x;
        let dy = e.clientY - pos.y;

        // Scroll the element
        ele.scrollTop = pos.top - dy;
        ele.scrollLeft = pos.left - dx;
    };

    let mouseUpHandler = function () {
        ele.style.cursor = "grab";
        ele.style.removeProperty("user-select");

        document.removeEventListener("mousemove", mouseMoveHandler);
        document.removeEventListener("mouseup", mouseUpHandler);
    };

    // Attach the handler
    ele.addEventListener("mousedown", mouseDownHandler);
});
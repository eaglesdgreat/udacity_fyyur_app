let venueItem = document.getElementById('delete-venue')
if(venueItem) {
    venueItem.onclick = function(e) {
        const venue_id = e.target.dataset.id;
        fetch(`/delete/venues/${venue_id}`, {method: 'DELETE'}).then(() => {
            window.location.href = '/'
        })
    }
}


let artistItem = document.getElementById('delete-artist')
if(artistItem) {
    artistItem.onclick = function(e) {
        const artist_id = e.target.dataset.id;
        fetch(`/delete/artists/${artist_id}`, {method: 'DELETE'}).then(() => {
            window.location.href = '/'
        })
    }
}

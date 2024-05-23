async function getRelatedArticles(query) {
    const response = await fetch("http://localhost:5555/api/related?cache=TRUE&query=" 
        + encodeURIComponent(query));
    
    return response.json();
}

function handleWidgetButtonClick() {
    const modalDiv = document.querySelector('.chat-widget-modal');
    const buttonDiv = document.querySelector('.chat-widget-button');

    modalDiv.classList.toggle('chat-widget-active');
    buttonDiv.classList.toggle('chat-widget-active');
}

async function handleWidgetSubmit(event) {
    event.preventDefault();
    const query = document.querySelector('.chat-widget-modal .chat-widget-input').value;
    const modalBody = document.querySelector('.chat-widget-modal .chat-widget-modal-body');
    const prevResults = document.querySelectorAll('.chat-widget-modal .chat-widget-result');

    // Clear previous results
    for (let i = 0; i < prevResults.length; i++) {
        prevResults[i].remove();
    }
    
    // Show empty query error
    if (query.length === 0) {
        const error = document.createElement('p');
        error.classList.add('chat-widget-result');
        error.innerHTML = 'Please type a question into the text box above.';
        modalBody.appendChild(error);
        return;
    }

    try {
        const relatedArticles = await getRelatedArticles(query);

        // error if no articles found
        if (relatedArticles.links.length === 0) {
            const error = document.createElement('p');
            error.classList.add('chat-widget-result');
            error.innerHTML = 'No articles found. Please reword your search.';
            modalBody.appendChild(error);
            return;
        }

        // list other articles found
        for (let i = 0; i < relatedArticles.links.length; i++) {
            const article = relatedArticles.links[i];
            const result = document.createElement('div');
            result.classList.add('chat-widget-result');

            const link = document.createElement('a');
            link.href = article.url;
            link.target = '_blank';
            link.innerHTML = `<b>${article.title}</b>`;
            result.appendChild(link);

            const formattedDate = new Date(article.date).toLocaleDateString('en-US', 
                { year: 'numeric', month: 'long', day: 'numeric' });
            const date = document.createElement('p');
            date.innerHTML = `(${formattedDate})`;
            result.appendChild(date);

            const description = document.createElement('p');
            description.innerHTML = article.description;
            result.appendChild(description);

            modalBody.appendChild(result);
        }
    } catch(err) {
        console.error(err);
        const error = document.createElement('p');
        error.classList.add('chat-widget-result');
        error.innerHTML = 'Our team is investigating some issues with the search assistant. Please try again later.';
        modalBody.appendChild(error);
        return;
    }
}

function init() {
    // Create containers
    const wrapper = document.createElement('div');
    const buttonDiv = document.createElement('div');
    const modalDiv = document.createElement('div');
    
    wrapper.appendChild(buttonDiv);
    wrapper.appendChild(modalDiv);

    // Class containers
    wrapper.classList.add('chat-widget-wrapper');
    buttonDiv.classList.add('chat-widget-button', 'chat-widget-active');
    modalDiv.classList.add('chat-widget-modal');

    // Init button
    buttonDiv.appendChild(document.createElement('button'));
    buttonDiv.firstChild.innerHTML = 
        '<img src="./widget/message-icon.svg" alt="Open article search assistant">';
    buttonDiv.firstChild.setAttribute('role', 'button');
    buttonDiv.firstChild.setAttribute('type', 'button');
    buttonDiv.firstChild.setAttribute('aria-label', 'Open article search assistant');
    buttonDiv.firstChild.setAttribute('title', 'Open article search assistant');
    buttonDiv.firstChild.addEventListener('click', handleWidgetButtonClick);

    // Init modal
    const modalTitleContainer = document.createElement('div');
    modalTitleContainer.classList.add('chat-widget-modal-title');
    modalDiv.appendChild(modalTitleContainer);
    const modalBodyContainer = document.createElement('div');
    modalBodyContainer.classList.add('chat-widget-modal-body');
    modalDiv.appendChild(modalBodyContainer);

    const modalTitle = document.createElement('h3');
    modalTitle.innerHTML = 'Article Search Assistant';
    modalTitleContainer.appendChild(modalTitle);

    const modalExit = document.createElement('button');
    modalExit.innerHTML = 'X';
    modalExit.classList.add('chat-widget-exit');
    modalExit.setAttribute('role', 'button');
    modalExit.setAttribute('type', 'button');
    modalExit.setAttribute('aria-label', 'Close article search assistant');
    modalExit.setAttribute('title', 'Close article search assistant');
    modalExit.addEventListener('click', handleWidgetButtonClick);
    modalDiv.appendChild(modalExit);

    const modalDesc = document.createElement('p');
    modalDesc.innerHTML = 'Ask a public health question to find relevant article(s)';
    modalBodyContainer.appendChild(modalDesc);

    const modalInput = document.createElement('textarea');
    modalInput.classList.add('chat-widget-input');
    modalInput.setAttribute('placeholder', 'Type your question here...');
    modalInput.setAttribute('maxlength', '300');
    modalBodyContainer.appendChild(modalInput);

    const modalSubmit = document.createElement('button');
    modalSubmit.innerHTML = 'Search';
    modalSubmit.classList.add('chat-widget-submit');
    modalSubmit.setAttribute('type', 'button');
    modalSubmit.setAttribute('role', 'button');
    modalSubmit.setAttribute('aria-label', 'Search for relevant articles');
    modalSubmit.setAttribute('title', 'Search for relevant articles');
    modalSubmit.addEventListener('click', handleWidgetSubmit);
    modalBodyContainer.appendChild(modalSubmit);

    // Space for future results
    const br = document.createElement('div');
    br.classList.add('chat-widget-br');
    modalBodyContainer.appendChild(br);

    // Add to DOM
    document.body.appendChild(wrapper);
}

document.addEventListener('DOMContentLoaded', init);
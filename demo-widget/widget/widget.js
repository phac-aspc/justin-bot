function encodeHtmlEntities(str) {
    return str.replace(/&/g, '&amp;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;')
              .replace(/"/g, '&quot;')
              .replace(/'/g, '&#39;')
              .replace(/\n/g, '<br>');
}

async function getRelatedArticles(query, aiSummary) {
    const modalBody = document.querySelector('.chat-widget-modal .chat-widget-modal-body');
    
    try {
        // Get data
        const response = await fetch(`http://localhost:5555/api/related?cache=${aiSummary ? "TRUE" : "FALSE"}&query=`
            + encodeURIComponent(query));
        const relatedArticles = await response.json();

        // error if no articles found
        if (!response.ok || relatedArticles.links.length === 0) {
            const error = document.createElement('p');
            error.classList.add('chat-widget-result');
            error.innerHTML = 'No articles found. Please reword your question.';
            modalBody.appendChild(error);
            return;
        }

        // list other articles found
        for (let i = 0; i < relatedArticles.links.length; i++) {
            const article = relatedArticles.links[i];
            const result = document.createElement('div');
            result.classList.add('chat-widget-result');

            // current article linked title
            const link = document.createElement('a');
            link.href = article.url;
            link.target = '_blank';
            link.innerHTML = `<b>${article.title}</b>`;
            result.appendChild(link);

            // current article date and description
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

        if (aiSummary) getAISummary(relatedArticles.id); // pass on next part
    } catch(err) {                                       // some network error
        console.error(err);                              // development only
        const error = document.createElement('p');
        error.classList.add('chat-widget-result');
        error.innerHTML = 'Our team is investigating some issues with the search assistant. Please try again later.';
        modalBody.appendChild(error);
        return;
    }
}

async function getAISummary(id) {
    const modalBody = document.querySelector('.chat-widget-modal .chat-widget-modal-body');
    
    try {
        // Get data
        const response = await fetch("http://localhost:5555/api/answer?id=" + id);
        
        if (!response.ok) {
            const error = document.createElement('p');
            error.classList.add('chat-widget-result');
            error.innerHTML = 'No computer-generated summary found. Please reword your question.';
            modalBody.appendChild(error);
            return;
        }

        const aiSummary = await response.json();

        // Show output
        const header = document.createElement('b');
        header.classList.add('chat-widget-result');
        header.innerHTML = 'Computer-generated summary:';
        modalBody.appendChild(header);

        const result = document.createElement('div');
        result.classList.add('chat-widget-result');
        result.innerHTML = encodeHtmlEntities(aiSummary.answer);
        modalBody.appendChild(result);

    } catch(err) {                                       // some network error
        console.error(err);                              // development only
        const error = document.createElement('p');
        error.classList.add('chat-widget-result');
        error.innerHTML = 'Our team is investigating some issues with the computer-generated summaries. Please try again later.';
        modalBody.appendChild(error);
        return;
    }
}

function handleWidgetButtonClick() {
    const modalDiv = document.querySelector('.chat-widget-modal');
    const buttonDiv = document.querySelector('.chat-widget-button');

    modalDiv.classList.toggle('chat-widget-active');
    buttonDiv.classList.toggle('chat-widget-active');
}

function handleWidgetSubmit(event) {
    event.preventDefault();
    const query = document.querySelector('.chat-widget-modal .chat-widget-input').value;
    const aiSummary = document.querySelector('.chat-widget-modal .chat-widget-checkbox').checked;
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

    getRelatedArticles(query, aiSummary);
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

    // Init button to open modal
    buttonDiv.appendChild(document.createElement('button'));
    buttonDiv.firstChild.innerHTML = 
        '<img src="./widget/message-icon.svg" alt="Open article search assistant">';
    buttonDiv.firstChild.setAttribute('role', 'button');
    buttonDiv.firstChild.setAttribute('type', 'button');
    buttonDiv.firstChild.setAttribute('aria-label', 'Open article search assistant');
    buttonDiv.firstChild.setAttribute('title', 'Open article search assistant');
    buttonDiv.firstChild.addEventListener('click', handleWidgetButtonClick);

    // Init modal (has title and body)
    const modalTitleContainer = document.createElement('div');
    modalTitleContainer.classList.add('chat-widget-modal-title');
    modalDiv.appendChild(modalTitleContainer);
    const modalBodyContainer = document.createElement('div');
    modalBodyContainer.classList.add('chat-widget-modal-body');
    modalDiv.appendChild(modalBodyContainer);

    // Init title text and close button
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

    // Init body text and question input
    const modalDesc = document.createElement('p');
    modalDesc.innerHTML = 'Ask a public health question to find relevant article(s)';
    modalBodyContainer.appendChild(modalDesc);

    const modalInput = document.createElement('textarea');
    modalInput.classList.add('chat-widget-input');
    modalInput.setAttribute('placeholder', 'Type your question here...');
    modalInput.setAttribute('maxlength', '300');
    modalBodyContainer.appendChild(modalInput);

    // Init checkbox and label to enable AI Q&A
    const enableAI = document.createElement('input');
    enableAI.classList.add('chat-widget-checkbox');
    enableAI.setAttribute('type', 'checkbox');
    enableAI.setAttribute('id', 'enableAI');
    enableAI.setAttribute('name', 'enableAI');
    enableAI.setAttribute('value', 'enableAI');
    modalBodyContainer.appendChild(enableAI);

    const enableAILabel = document.createElement('label');
    enableAILabel.setAttribute('for', 'enableAI');
    enableAILabel.classList.add('chat-widget-label');
    enableAILabel.innerHTML = 'Create computer-generated answer (experimental)';
    modalBodyContainer.appendChild(enableAILabel);

    // Init submit button
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
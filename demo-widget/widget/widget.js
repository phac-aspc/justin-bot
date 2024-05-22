function handleWidgetButtonClick() {
    const modalDiv = document.querySelector('.chat-widget-modal');
    const buttonDiv = document.querySelector('.chat-widget-button');

    modalDiv.classList.toggle('chat-widget-active');
    buttonDiv.classList.toggle('chat-widget-active');
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
    modalBodyContainer.appendChild(modalInput);

    const modalSubmit = document.createElement('button');
    modalSubmit.innerHTML = 'Search';
    modalSubmit.classList.add('chat-widget-submit');
    modalSubmit.setAttribute('type', 'button');
    modalSubmit.setAttribute('role', 'button');
    modalSubmit.setAttribute('aria-label', 'Search for relevant articles');
    modalSubmit.setAttribute('title', 'Search for relevant articles');
    modalBodyContainer.appendChild(modalSubmit);

    // Add to DOM
    document.body.appendChild(wrapper);
}

document.addEventListener('DOMContentLoaded', init);
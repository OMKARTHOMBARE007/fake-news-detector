$(document).ready(function() {
    // File upload preview
    $('#mediaFile').on('change', function(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        const preview = $('#mediaPreview');
        const imagePreview = $('#imagePreview');
        const videoPreview = $('#videoPreview');
        
        preview.show();
        
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.attr('src', e.target.result).show();
                videoPreview.hide();
            };
            reader.readAsDataURL(file);
        } else if (file.type.startsWith('video/')) {
            videoPreview.attr('src', URL.createObjectURL(file)).show();
            imagePreview.hide();
        }
    });
    
    // Fake News Text Analysis
    $('#textAnalysisForm').on('submit', function(e) {
        e.preventDefault();
        
        const text = $('#newsText').val().trim();
        const method = $('#detectionMethod').val();
        
        if (!text) {
            alert('Please enter text to analyze');
            return;
        }
        
        showLoading('#newsResults');
        
        $.ajax({
            url: '/detect-news',
            method: 'POST',
            data: {
                data_type: 'text',
                text: text,
                detection_method: method
            },
            success: function(response) {
                displayNewsResults(response);
            },
            error: function(xhr) {
                showError('#newsResults', xhr.responseJSON?.error || 'Analysis failed');
            }
        });
    });
    
    // URL Analysis
    $('#urlAnalysisForm').on('submit', function(e) {
        e.preventDefault();
        
        const url = $('#newsUrl').val().trim();
        
        if (!url) {
            alert('Please enter a URL');
            return;
        }
        
        showLoading('#newsResults');
        
        $.ajax({
            url: '/detect-news',
            method: 'POST',
            data: {
                data_type: 'url',
                url: url
            },
            success: function(response) {
                displayNewsResults(response);
            },
            error: function(xhr) {
                showError('#newsResults', xhr.responseJSON?.error || 'URL analysis failed');
            }
        });
    });
    
    // Deepfake Detection
    $('#deepfakeForm').on('submit', function(e) {
        e.preventDefault();
        
        const fileInput = $('#mediaFile')[0];
        if (!fileInput.files.length) {
            alert('Please select a file');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        
        showLoading('#deepfakeResults');
        
        $.ajax({
            url: '/detect-deepfake',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                displayDeepfakeResults(response);
            },
            error: function(xhr) {
                showError('#deepfakeResults', xhr.responseJSON?.error || 'Deepfake detection failed');
            }
        });
    });
    
    // Display News Results
    function displayNewsResults(result) {
        const container = $('#newsResults');
        let html = '';
        
        if (result.error) {
            html = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i> ${result.error}
                </div>
            `;
        } else {
            const isFake = result.prediction === 'Fake';
            const confidence = (result.confidence * 100).toFixed(1);
            const fakeProb = (result.fake_probability * 100).toFixed(1);
            const realProb = (result.real_probability * 100).toFixed(1);
            
            html = `
                <div class="result-card ${isFake ? 'result-fake' : 'result-real'}">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h4 class="mb-0">
                            <i class="fas ${isFake ? 'fa-times-circle text-danger' : 'fa-check-circle text-success'}"></i>
                            ${result.prediction} News
                        </h4>
                        <span class="badge bg-${isFake ? 'danger' : 'success'}">${confidence}% Confidence</span>
                    </div>
                    
                    <div class="mb-3">
                        <strong>Method:</strong> ${result.method || 'N/A'}
                    </div>
                    
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-body">
                                    <h6>Fake Probability</h6>
                                    <div class="progress">
                                        <div class="progress-bar bg-danger" style="width: ${fakeProb}%">${fakeProb}%</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-body">
                                    <h6>Real Probability</h6>
                                    <div class="progress">
                                        <div class="progress-bar bg-success" style="width: ${realProb}%">${realProb}%</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    ${result.warnings && result.warnings.length ? `
                        <div class="alert alert-warning">
                            <h6><i class="fas fa-exclamation-triangle"></i> Warnings:</h6>
                            <ul class="mb-0">
                                ${result.warnings.map(warning => `<li>${warning}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                    
                    ${result.linguistic_features ? `
                        <div class="mt-3">
                            <h6><i class="fas fa-chart-bar"></i> Linguistic Analysis:</h6>
                            <div class="row small">
                                ${Object.entries(result.linguistic_features).map(([key, value]) => `
                                    <div class="col-6 col-md-4 mb-1">
                                        <strong>${formatKey(key)}:</strong> ${typeof value === 'number' ? value.toFixed(3) : value}
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                    
                    ${result.text ? `
                        <div class="mt-3">
                            <h6><i class="fas fa-file-alt"></i> Analyzed Text:</h6>
                            <div class="text-muted small">
                                ${result.text.length > 300 ? result.text.substring(0, 300) + '...' : result.text}
                            </div>
                        </div>
                    ` : ''}
                </div>
            `;
        }
        
        container.html(html).show();
    }
    
    // Display Deepfake Results
    function displayDeepfakeResults(result) {
        const container = $('#deepfakeResults');
        let html = '';
        
        if (result.error) {
            html = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i> ${result.error}
                </div>
            `;
        } else {
            const isFake = result.prediction === 'Fake';
            const confidence = (result.confidence * 100).toFixed(1);
            const fakeProb = (result.fake_probability * 100).toFixed(1);
            
            html = `
                <div class="result-card ${isFake ? 'result-fake' : 'result-real'}">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h4 class="mb-0">
                            <i class="fas ${isFake ? 'fa-robot text-danger' : 'fa-user-check text-success'}"></i>
                            ${result.prediction} Media
                        </h4>
                        <span class="badge bg-${isFake ? 'danger' : 'success'}">${confidence}% Confidence</span>
                    </div>
                    
                    <div class="mb-3">
                        <strong>Analysis Type:</strong> ${result.file_type === 'image' ? 'Image Analysis' : 'Video Analysis'}
                        ${result.faces_detected ? ` | <strong>Faces Detected:</strong> ${result.faces_detected}` : ''}
                        ${result.frames_analyzed ? ` | <strong>Frames Analyzed:</strong> ${result.frames_analyzed}` : ''}
                    </div>
                    
                    <div class="mb-3">
                        <div class="d-flex align-items-center mb-2">
                            <strong class="me-2">Deepfake Score:</strong>
                            <span class="badge bg-${fakeProb > 60 ? 'danger' : fakeProb > 30 ? 'warning' : 'success'}">
                                ${fakeProb}%
                            </span>
                        </div>
                        <div class="progress">
                            <div class="progress-bar bg-danger" style="width: ${fakeProb}%"></div>
                        </div>
                    </div>
                    
                    ${result.details && result.details.length ? `
                        <div class="mt-3">
                            <h6><i class="fas fa-user-circle"></i> Face Analysis:</h6>
                            ${result.details.map(face => `
                                <div class="card mb-2">
                                    <div class="card-body p-3">
                                        <div class="d-flex justify-content-between">
                                            <span>Face ${face.face_id}</span>
                                            <span class="badge bg-${face.is_fake ? 'danger' : 'success'}">
                                                ${(face.fake_score * 100).toFixed(1)}% Fake
                                            </span>
                                        </div>
                                        <div class="small text-muted">
                                            Position: (${face.position.x}, ${face.position.y})
                                        </div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                    
                    ${result.frame_details && result.frame_details.length ? `
                        <div class="mt-3">
                            <h6><i class="fas fa-film"></i> Frame Analysis:</h6>
                            <div class="table-responsive">
                                <table class="table table-sm">
                                    <thead>
                                        <tr>
                                            <th>Frame</th>
                                            <th>Faces</th>
                                            <th>Fake Score</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${result.frame_details.map(frame => `
                                            <tr>
                                                <td>${frame.frame}</td>
                                                <td>${frame.faces_detected}</td>
                                                <td>
                                                    <span class="badge bg-${frame.fake_score > 0.6 ? 'danger' : 'success'}">
                                                        ${(frame.fake_score * 100).toFixed(1)}%
                                                    </span>
                                                </td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    ` : ''}
                </div>
            `;
        }
        
        container.html(html).show();
    }
    
    // Helper Functions
    function showLoading(selector) {
        $(selector).html(`
            <div class="text-center py-4">
                <div class="loading mx-auto mb-3"></div>
                <p>Analyzing content...</p>
            </div>
        `).show();
    }
    
    function showError(selector, message) {
        $(selector).html(`
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle"></i> ${message}
            </div>
        `).show();
    }
    
    function formatKey(key) {
        return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
    
    // Tab functionality
    $('.nav-tabs button').on('click', function() {
        $('.nav-tabs button').removeClass('active');
        $(this).addClass('active');
    });
});
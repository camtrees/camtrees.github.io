/**
 * CAMTREES public data-request receiver.
 *
 * Deploy this project as a Google Apps Script web app that executes as the
 * camorg.database@gmail.com owner. Public forms send ordinary form fields to
 * doPost(); no Gmail or database credentials belong in the GitHub Pages site.
 */

/**
 * Server-side allow-list for every accepted request type and field.
 *
 * Add future new_organization, new_hub, or new_volunteer definitions here.
 * Keeping a separate server-side list is intentional: browser-submitted field
 * names cannot be trusted, even though the page has its own YAML definition.
 */
// These fields are appended to request types that need requestor information.
// The browser form mirrors them from _data/request_form_sections.yml.
const REQUESTOR_FIELDS = Object.freeze([
  { name: 'requestor_name', label: "Requestor's Name", maximumLength: 200 },
  { name: 'requestor_email', label: "Requestor's Email", maximumLength: 320 },
  { name: 'requestor_phone', label: "Requestor's Phone", maximumLength: 100 },
  { name: 'comments', label: 'Additional Comments', maximumLength: 1000 }
]);

// This reminder appears at the bottom of every New Data Request email.
const COMMON_EMAIL_FOOTER =
  'Please review this New Data Request before adding it to the CAMTREES SQL Database.';

const REQUEST_DEFINITIONS = Object.freeze({
  new_site: {
    label: 'New Site',
    subjectField: 'site_name',
    additionalFooter: "Please add a 'CAM Org - Site Name' record to both the 'CAM Trees Maintenance' and 'CAM Trees Rain Event' EpiCollect projects.",
    requiredFields: ['site_name', 'hub', 'organization_code', 'organization_name', 'town', 'contact_name', 'contact_email', 'requestor_name', 'requestor_email'],
    replyToField: 'requestor_email',
    emailFields: ['contact_email', 'primary_caretaker_email', 'secondary_caretaker_email', 'requestor_email'],
    fields: [
      { name: 'site_name', label: 'Site Name', maximumLength: 200 },
      { name: 'hub', label: 'Hub', maximumLength: 200 },
      { name: 'organization_code', label: 'Organization Code', maximumLength: 100 },
      { name: 'organization_name', label: 'Organization Name', maximumLength: 200 },
      { name: 'town', label: 'Town', maximumLength: 200 },
      { name: 'site_location', label: 'Site Location', maximumLength: 500 },
      { name: 'location_note', label: 'Location Note', maximumLength: 1000 },
      { name: 'contact_name', label: 'Contact Name', maximumLength: 200 },
      { name: 'contact_email', label: 'Contact Email', maximumLength: 320 },
      { name: 'site_url', label: 'Site URL', maximumLength: 500 },
      { name: 'primary_caretaker_name', label: 'Primary Caretaker Name', maximumLength: 200 },
      { name: 'primary_caretaker_email', label: 'Primary Caretaker Email', maximumLength: 320 },
      { name: 'secondary_caretaker_name', label: 'Secondary Caretaker Name', maximumLength: 200 },
      { name: 'secondary_caretaker_email', label: 'Secondary Caretaker Email', maximumLength: 320 }
    ].concat(REQUESTOR_FIELDS)
  },
  new_hub: {
    label: 'New Hub',
    subjectField: 'hub_name',
    additionalFooter: "Please add the Captain and Lieutenant to the 'Google Hub Captains' group and the EpiCollect 'CAM Trees Rain Event' project as a collaborator.",
    requiredFields: ['hub_name', 'requestor_name', 'requestor_email'],
    replyToField: 'requestor_email',
    emailFields: ['captain_email', 'lieutenant_email', 'requestor_email'],
    fields: [
      { name: 'hub_name', label: 'Hub Name', maximumLength: 200 },
      { name: 'captain_name', label: 'Captain Name', maximumLength: 200 },
      { name: 'captain_email', label: 'Captain Email', maximumLength: 320 },
      { name: 'lieutenant_name', label: 'Lieutenant Name', maximumLength: 200 },
      { name: 'lieutenant_email', label: 'Lieutenant Email', maximumLength: 320 }
    ].concat(REQUESTOR_FIELDS)
  },
  new_cam_org: {
    label: 'New Cam Org',
    subjectField: 'cam_org_code',
    requiredFields: ['cam_org_code', 'cam_org_name', 'cam_org_contact_name', 'cam_org_contact_email', 'requestor_name', 'requestor_email'],
    replyToField: 'requestor_email',
    emailFields: ['cam_org_contact_email', 'requestor_email'],
    fields: [
      { name: 'cam_org_code', label: 'Cam Org Code', maximumLength: 100 },
      { name: 'cam_org_name', label: 'Cam Org Name', maximumLength: 200 },
      { name: 'cam_org_contact_name', label: 'Cam Org Contact Name', maximumLength: 200 },
      { name: 'cam_org_contact_email', label: 'Cam Org Contact Email', maximumLength: 320 }
    ].concat(REQUESTOR_FIELDS)
  },
  new_volunteer: {
    label: 'New Volunteer',
    subjectField: 'volunteer_name',
    additionalFooter: "Please add the New Volunteer to the 'CAM Tree Maintenance' project as a collaborator.",
    requiredFields: ['volunteer_name', 'volunteer_email', 'requestor_name', 'requestor_email'],
    replyToField: 'requestor_email',
    emailFields: ['volunteer_email', 'requestor_email'],
    fields: [
      { name: 'volunteer_name', label: 'Volunteer Name', maximumLength: 200 },
      { name: 'volunteer_email', label: 'Volunteer Email', maximumLength: 320 },
      { name: 'cell_phone', label: 'Cell Phone', maximumLength: 100 },
      { name: 'home_phone', label: 'Home Phone', maximumLength: 100 },
      { name: 'work_phone', label: 'Work Phone', maximumLength: 100 },
      { name: 'job_title', label: 'Job Title', maximumLength: 200 },
      { name: 'hometown', label: 'Hometown', maximumLength: 200 }
    ].concat(REQUESTOR_FIELDS)
  },
  new_parent_tree: {
    label: 'New Parent Tree',
    subjectField: 'parent_tree',
    additionalFooter: 'Please add the new Parent Tree to the appropriate EpiCollect project(s).',
    requiredFields: ['parent_tree', 'requestor_name', 'requestor_email'],
    replyToField: 'requestor_email',
    emailFields: ['requestor_email'],
    fields: [
      { name: 'parent_tree', label: 'Parent Tree', maximumLength: 200 }
    ].concat(REQUESTOR_FIELDS)
  }
});


/**
 * Receive one form submission, validate it, and email it to the administrator.
 */
function doPost(event) {
  try {
    const parameters = event && event.parameter ? event.parameter : {};

    // Bots commonly complete this off-screen field. Return an ordinary success
    // page so the response does not teach a bot how the trap works.
    if (normalizeValue(parameters.website, 200)) {
      return resultPage(
        'Request received',
        'Thank you. Your request has been received.'
      );
    }

    const requestType = normalizeValue(parameters.request_type, 100);
    const definition = REQUEST_DEFINITIONS[requestType];
    if (!definition) {
      throw new Error('Unknown or missing request_type.');
    }

    // Copy only known fields into the request. Unexpected browser parameters
    // never enter the email message.
    const request = {};
    definition.fields.forEach(function(field) {
      request[field.name] = normalizeValue(
        parameters[field.name],
        field.maximumLength
      );
    });

    validateRequest(definition, request);

    const scriptProperties = PropertiesService.getScriptProperties();
    const administratorEmail = scriptProperties.getProperty(
      'DATABASE_ADMINISTRATOR_EMAIL'
    );
    if (!isValidEmail(administratorEmail)) {
      throw new Error(
        'DATABASE_ADMINISTRATOR_EMAIL is missing or invalid.'
      );
    }

    const requestId = Utilities.getUuid();
    const submittedAt = Utilities.formatDate(
      new Date(),
      'America/New_York',
      "MMMM d, yyyy 'at' h:mm a z"
    );
    const subjectValue = singleLine(
      request[definition.subjectField] || 'Unnamed request'
    );
    const subject = 'CAMTREES ' + definition.label + ' Request: ' + subjectValue;
    const textBody = buildTextBody(
      definition,
      request,
      requestId,
      submittedAt
    );
    const htmlBody = buildHtmlBody(
      definition,
      request,
      requestId,
      submittedAt
    );

    const message = {
      to: administratorEmail,
      subject: subject,
      body: textBody,
      htmlBody: htmlBody,
      name: 'CAMTREES Data Requests'
    };

    // Replies go to the requestor, while the message itself remains sent by
    // the Google account that owns and executes this Apps Script deployment.
    const replyTo = request[definition.replyToField];
    if (isValidEmail(replyTo)) {
      message.replyTo = replyTo;
    }

    MailApp.sendEmail(message);

    return resultPage(
      'Request submitted',
      'Thank you. Your request has been sent to the CAMTREES Database Administrator.'
    );
  } catch (error) {
    console.error(error && error.stack ? error.stack : error);
    return resultPage(
      'Unable to submit request',
      'The request could not be sent. Please return to the form and try again.'
    );
  }
}


/**
 * Reject incomplete requests and invalid requestor email addresses.
 */
function validateRequest(definition, request) {
  definition.requiredFields.forEach(function(fieldName) {
    if (!request[fieldName]) {
      throw new Error('A required field is missing: ' + fieldName);
    }
  });

  if (
    definition.replyToField &&
    !isValidEmail(request[definition.replyToField])
  ) {
    throw new Error('The requestor email address is invalid.');
  }

  // Validate optional email fields only when the user supplied a value.
  (definition.emailFields || []).forEach(function(fieldName) {
    if (request[fieldName] && !isValidEmail(request[fieldName])) {
      throw new Error('An email address is invalid: ' + fieldName);
    }
  });
}


/**
 * Build a readable plain-text alternative for every email client.
 */
function buildTextBody(definition, request, requestId, submittedAt) {
  const lines = [
    'CAMTREES ' + definition.label + ' Request',
    ''
  ];

  definition.fields.forEach(function(field) {
    // Visually separate the reusable requestor details from record-specific data.
    if (field.name === 'requestor_name') {
      lines.push('');
    }
    lines.push(field.label + ' : ' + displayValue(request[field.name]));
  });

  lines.push('');
  lines.push('Request ID : ' + requestId);
  lines.push('Submitted : ' + submittedAt);

  // Put the common review reminder and any request-specific action at the end.
  lines.push('');
  emailFooterLines(definition).forEach(function(line) {
    lines.push(line);
  });
  return lines.join('\n');
}


/**
 * Build the formatted table shown by HTML-capable email clients.
 */
function buildHtmlBody(definition, request, requestId, submittedAt) {
  const rows = [];

  definition.fields.forEach(function(field) {
    // Introduce the reusable requestor details with a compact section heading.
    if (field.name === 'requestor_name') {
      rows.push(emailSectionRow('Requested By...'));
    }
    rows.push(emailRow(field.label, displayValue(request[field.name])));
  });

  rows.push(emailRow('Request ID', requestId));
  rows.push(emailRow('Submitted', submittedAt));

  const footerParagraphs = emailFooterLines(definition).map(function(line) {
    return '<p style="margin:.5rem 0">' + escapeHtml(line) + '</p>';
  });

  return [
    '<h2>CAMTREES ' + escapeHtml(definition.label) + ' Request</h2>',
    '<table cellpadding="6" cellspacing="0" style="border-collapse:collapse">',
    rows.join(''),
    '</table>',
    '<div style="margin-top:1rem;padding-top:.5rem;border-top:1px solid #cccccc">',
    footerParagraphs.join(''),
    '</div>'
  ].join('');
}


/**
 * Return the universal footer followed by an optional request-specific action.
 */
function emailFooterLines(definition) {
  const lines = [COMMON_EMAIL_FOOTER];
  if (definition.additionalFooter) {
    lines.push(definition.additionalFooter);
  }
  return lines;
}


/**
 * Create a compact heading that spans both columns of the HTML email table.
 */
function emailSectionRow(label) {
  return [
    '<tr>',
    '<th colspan="2" align="left" ',
    'style="padding-top:1rem;border-bottom:1px solid #5b765c;font-size:.95rem">',
    escapeHtml(label),
    '</th>',
    '</tr>'
  ].join('');
}


/**
 * Create one safely escaped label/value row for the HTML email.
 */
function emailRow(label, value) {
  return [
    '<tr>',
    '<th align="left" valign="top" ',
    'style="border:1px solid #cccccc;background:#e8f5e9">',
    escapeHtml(label) + ' :',
    '</th>',
    '<td style="border:1px solid #cccccc">',
    escapeHtml(value).replace(/\n/g, '<br>'),
    '</td>',
    '</tr>'
  ].join('');
}


/**
 * Normalize a browser value and enforce the field's maximum length again on
 * the server. HTML maxlength attributes alone are not a security boundary.
 */
function normalizeValue(value, maximumLength) {
  return String(value || '').trim().substring(0, maximumLength || 5000);
}


/**
 * Keep an email subject on one line.
 */
function singleLine(value) {
  return String(value || '').replace(/[\r\n]+/g, ' ').trim();
}


function displayValue(value) {
  return value || '(not provided)';
}


function isValidEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(value || ''));
}


/**
 * Escape untrusted form values before placing them into HTML.
 */
function escapeHtml(value) {
  return String(value || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}


/**
 * Return a small confirmation page after the browser leaves the form page.
 */
function resultPage(title, message) {
  const configuredUrl = PropertiesService.getScriptProperties()
    .getProperty('CAMTREES_RETURN_URL');
  const returnUrl = configuredUrl || 'https://camtrees.github.io/';

  return HtmlService.createHtmlOutput([
    '<!doctype html><html lang="en"><head>',
    // Apps Script displays HtmlService output in a sandboxed iframe. Make the
    // return link replace the full browser page instead of only that iframe.
    '<base target="_top">',
    '<meta charset="utf-8">',
    '<meta name="viewport" content="width=device-width,initial-scale=1">',
    '<title>' + escapeHtml(title) + '</title>',
    '<style>',
    'body{max-width:42rem;margin:3rem auto;padding:1rem;',
    'font-family:system-ui,sans-serif;line-height:1.5}',
    'a{display:inline-block;margin-top:1rem;padding:.6rem 1rem;color:#222;',
    'background:#e8f5e9;border:1px solid #5b765c;border-radius:.3rem}',
    '</style></head><body>',
    '<h1>' + escapeHtml(title) + '</h1>',
    '<p>' + escapeHtml(message) + '</p>',
    '<a target="_top" href="' + escapeHtml(returnUrl) + '">Return to the CAMTREES website</a>',
    '</body></html>'
  ].join(''));
}

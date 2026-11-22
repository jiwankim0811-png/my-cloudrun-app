/**
 * ==============================================================================
 * Google Apps Script (GAS) - BFS vs DFS 미로 탐색 시각화 컨트롤러 (Code.gs)
 * Stitch 프로젝트 연동: projects/17197904467986631939 (BFS vs DFS Maze Visualizer)
 * ==============================================================================
 */

/**
 * 웹 앱 진입점: 사용자가 웹 앱 URL에 접속할 때 index.html을 렌더링합니다.
 * @param {Object} e - HTTP GET 이벤트 객체
 * @return {HtmlOutput} 브라우저로 전달될 HTML 페이지
 */
function doGet(e) {
  try {
    const template = HtmlService.createTemplateFromFile('index');
    template.projectId = 'projects/17197904467986631939';
    const propUrl = PropertiesService.getScriptProperties().getProperty('SERVICE_URL');
    template.defaultServerUrl = propUrl || 'https://my-cloudrun-app-786158012233.us-central1.run.app';

    const htmlOutput = template.evaluate()
      .setTitle('GraphLab: BFS vs DFS Maze Escape Benchmark | Queue vs Stack 시각화')
      .addMetaTag('viewport', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no')
      .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);

    return htmlOutput;
  } catch (error) {
    Logger.log('[doGet 오류] ' + error.toString());
    return HtmlService.createHtmlOutput(
      '<div style="font-family:sans-serif; padding:20px; color:#d93025; background:#051424;">' +
      '<h3>웹 애플리케이션 초기화 실패</h3>' +
      '<p>' + error.message + '</p>' +
      '</div>'
    );
  }
}

/**
 * 웹훅 엔드포인트: Cloud Run 배포 완료 후 전달된 서비스 URL을 PropertiesService에 저장합니다.
 * @param {Object} e - HTTP POST 이벤트 객체
 * @return {TextOutput} JSON 응답
 */
function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const serviceUrl = data.serviceUrl || data.url;
    if (serviceUrl) {
      PropertiesService.getScriptProperties().setProperty('SERVICE_URL', serviceUrl);
      return ContentService.createTextOutput(JSON.stringify({ status: 'ok', serviceUrl: serviceUrl }))
        .setMimeType(ContentService.MimeType.JSON);
    }
    return ContentService.createTextOutput(JSON.stringify({ status: 'ignored', reason: 'No serviceUrl provided' }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ status: 'error', message: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * Cloud Run 백엔드 API로 BFS vs DFS 미로 풀이 요청을 프록시 전송합니다.
 * @param {string} serverUrl - Cloud Run 또는 로컬 백엔드 서버 URL
 * @param {string} preset - 미로 프리셋 ('classic', 'dense', 'bottleneck')
 * @return {Object} 백엔드에서 반환된 단계별 히스토그램 스냅샷 및 비교 결과
 */
function fetchMazeSimulationFromBackend(serverUrl, preset) {
  if (!serverUrl || typeof serverUrl !== 'string') {
    return { success: false, error: '유효한 백엔드 서버 URL이 전달되지 않았습니다.' };
  }

  const endpoint = serverUrl.replace(/\/+$/, '') + '/solve';
  const payload = {
    preset: preset || 'classic',
    start: [0, 0],
    goal: [9, 9]
  };

  const options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  try {
    const response = UrlFetchApp.fetch(endpoint, options);
    const statusCode = response.getResponseCode();
    const contentText = response.getContentText();

    if (statusCode >= 200 && statusCode < 300) {
      const data = JSON.parse(contentText);
      return { success: true, data: data };
    } else {
      return {
        success: false,
        statusCode: statusCode,
        error: '백엔드 서버 오류 (HTTP ' + statusCode + '): ' + contentText
      };
    }
  } catch (err) {
    Logger.log('[fetchMazeSimulationFromBackend 실패] ' + err.toString());
    return {
      success: false,
      error: '백엔드 통신 실패: ' + err.message
    };
  }
}

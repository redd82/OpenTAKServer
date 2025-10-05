


def _start_injection(camera_source_url, camera_uid, link_uid):
    """
    -----------------------------------------------------------------------------------------
    COT MEssage with a streaming link
    -----------------------------------------------------------------------------------------
    <?xml version="1.0" encoding="UTF-8"?>
        <event version="2.0"
            uid="phone-123e4567-e89b-12d3-a456-426614174000"
            type="a-f-G-U-C"                 <!-- camera / video sensor -->
            how="m-g"                        <!-- machine generated -->
            time="2025-10-04T12:34:56.000Z"  <!-- timestamp of message -->
            start="2025-10-04T12:34:56.000Z"
            stale="2025-10-04T12:39:56.000Z"> <!-- stale after 5 minutes -->
            <!-- Geolocation of the phone / camera -->
            <point lat="52.370216" lon="4.895168" hae="10.0" ce="30.0" le="30.0"/>
            
            <detail>
                <!-- Who / what is streaming -->
                <contact callsign="AlicePhone" type="person"/>
                <__device model="Pixel 7" os="Android 14" app="MobileStreamer/1.2.3"/>
                
                <!-- Primary video stream link (RTSP example) -->
                <link relation="stream" type="application/sdp">
                rtsp://192.0.2.45:8554/live/stream1
                </link>

                <!-- Alternative stream (HLS) -->
                <link relation="stream" type="application/vnd.apple.mpegurl">
                https://media.example.org/hls/alicephone/stream.m3u8
                </link>

                <!-- A short human-readable description -->
                <remarks>
                Live video from phone camera. Stabilized, 1080p30. Viewer auth required.
                </remarks>

                <!-- Some custom metadata (non-standard CoT extension element) -->
                <__metadata>
                <bitrate>2500kbps</bitrate>
                <orientation>portrait</orientation>
                <facing>rear</facing>
                <encryption>SRTP</encryption>
                </__metadata>
            </detail>
        </event>
        
        -----------------------------------------------------------------------------------------       
        COT message without a streaming link  (it treamed in the past tho)
        -----------------------------------------------------------------------------------------        
        <?xml version="1.0" encoding="UTF-8"?>
            <event version="2.0"
                uid="phone-123e4567-e89b-12d3-a456-426614174000"
                type="a-f-G-U-C"                 <!-- still the same device type -->
                how="m-g"
                time="2025-10-04T12:42:10.000Z"
                start="2025-10-04T12:42:10.000Z"
                stale="2025-10-04T12:47:10.000Z">
                
                <!-- Device’s last known position -->
                <point lat="52.370220" lon="4.895175" hae="9.8" ce="25.0" le="25.0"/>

                <detail>
                    <contact callsign="AlicePhone" type="person"/>
                    <__device model="Pixel 7" os="Android 14" app="MobileStreamer/1.2.3"/>

                    <!-- No active stream link -->
                    <remarks>
                    Device online — no active video stream. Camera app idle.
                    </remarks>

                    <!-- Optional state marker -->
                    <__metadata>
                    <stream_active>false</stream_active>
                    <last_stream_uri>rtsp://192.0.2.45:8554/live/stream1</last_stream_uri>
                    <battery>84%</battery>
                    <network>wifi</network>
                    </__metadata>
                </detail>
            </event>
        
        -----------------------------------------------------------------------------------------       
        COT message device never had a stream
        -----------------------------------------------------------------------------------------
        <?xml version="1.0" encoding="UTF-8"?>
            <event version="2.0"
                uid="phone-123e4567-e89b-12d3-a456-426614174000"
                type="a-f-G-U-C"                 <!-- Android user / civilian -->
                how="m-g"
                time="2025-10-04T12:50:15.000Z"
                start="2025-10-04T12:50:15.000Z"
                stale="2025-10-04T12:55:15.000Z">
            <point lat="52.370216" lon="4.895168" hae="8.2" ce="20.0" le="20.0"/>

            <detail>
                <contact callsign="AlicePhone" type="person"/>
                <__device model="Pixel 7" os="Android 14" app="MobileTracker/1.0.0"/>
                <status battery="87%" network="wifi"/>
            </detail>
            </event>
    """
    # Placeholder for starting injection logic
    
    
    pass            
def _stop_injection(camera_uid, link_uid):
    # Placeholder for stopping injection logic
    pass    


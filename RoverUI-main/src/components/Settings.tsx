import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Switch } from './ui/switch';
import { Label } from './ui/label';
import { Progress } from './ui/progress';
import { Separator } from './ui/separator';
import { Slider } from './ui/slider';
import { Wifi, Radio, Zap, Battery, Download, Settings2, Gauge, Droplet } from 'lucide-react';
import { useState } from 'react';

export function Settings() {
  const [autoTreatment, setAutoTreatment] = useState(false);
  const [notifications, setNotifications] = useState(true);
  const [nightMode, setNightMode] = useState(false);
  const [waterThreshold, setWaterThreshold] = useState([30]);
  const [scanFrequency, setScanFrequency] = useState([60]);

  return (
    <div className="space-y-6">
      {/* Connection Status */}
      <Card className="p-6">
        <div className="flex items-center gap-2 mb-6">
          <Wifi className="w-5 h-5 text-[#4CAF50]" />
          <h3>Connection Status</h3>
        </div>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="mb-1">Wi-Fi Connection</p>
              <p className="text-sm text-muted-foreground">AgriNet-5G</p>
            </div>
            <Badge className="bg-[#4CAF50]">
              <div className="w-2 h-2 bg-white rounded-full mr-2 animate-pulse" />
              Connected
            </Badge>
          </div>
          <Separator />
          <div className="flex items-center justify-between">
            <div>
              <p className="mb-1">MQTT Broker</p>
              <p className="text-sm text-muted-foreground">mqtt.agriserver.local:1883</p>
            </div>
            <Badge className="bg-[#4CAF50]">
              <div className="w-2 h-2 bg-white rounded-full mr-2 animate-pulse" />
              Active
            </Badge>
          </div>
          <Separator />
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Radio className="w-4 h-4" />
              <div>
                <p className="mb-1">Signal Strength</p>
                <p className="text-sm text-muted-foreground">Excellent</p>
              </div>
            </div>
            <div className="text-right">
              <p>-42 dBm</p>
              <Progress value={85} className="w-24 h-2 mt-1" />
            </div>
          </div>
        </div>
      </Card>

      {/* System Information */}
      <Card className="p-6">
        <div className="flex items-center gap-2 mb-6">
          <Settings2 className="w-5 h-5 text-[#4CAF50]" />
          <h3>System Information</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <p className="text-sm text-muted-foreground mb-1">Firmware Version</p>
            <p className="mb-3">v2.4.1</p>
            <Button variant="outline" size="sm">
              <Download className="w-4 h-4 mr-2" />
              Check for Updates
            </Button>
          </div>
          <div>
            <p className="text-sm text-muted-foreground mb-1">Last Updated</p>
            <p className="mb-3">October 10, 2025</p>
            <Badge variant="outline" className="text-[#4CAF50] border-[#4CAF50]">
              Up to date
            </Badge>
          </div>
          <div>
            <p className="text-sm text-muted-foreground mb-1">Serial Number</p>
            <p>AGR-2024-X7291</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground mb-1">Uptime</p>
            <p>12d 8h 42m</p>
          </div>
        </div>
      </Card>

      {/* Sensor Calibration */}
      <Card className="p-6">
        <div className="flex items-center gap-2 mb-6">
          <Gauge className="w-5 h-5 text-[#4CAF50]" />
          <h3>Sensor Calibration</h3>
        </div>
        <div className="space-y-6">
          <div>
            <div className="flex items-center justify-between mb-3">
              <Label>Water Stress Detection Threshold</Label>
              <Badge variant="outline">{waterThreshold[0]}%</Badge>
            </div>
            <Slider
              value={waterThreshold}
              onValueChange={setWaterThreshold}
              max={100}
              step={5}
              className="mb-2"
            />
            <p className="text-sm text-muted-foreground">
              Alert when soil moisture drops below this level
            </p>
          </div>
          
          <Separator />
          
          <div>
            <div className="flex items-center justify-between mb-3">
              <Label>Scan Frequency</Label>
              <Badge variant="outline">{scanFrequency[0]} min</Badge>
            </div>
            <Slider
              value={scanFrequency}
              onValueChange={setScanFrequency}
              min={15}
              max={180}
              step={15}
              className="mb-2"
            />
            <p className="text-sm text-muted-foreground">
              Time between automatic field scans
            </p>
          </div>

          <Separator />

          <div className="grid grid-cols-2 gap-3">
            <Button variant="outline" size="sm">
              Calibrate Moisture Sensor
            </Button>
            <Button variant="outline" size="sm">
              Calibrate Camera
            </Button>
            <Button variant="outline" size="sm">
              Calibrate GPS
            </Button>
            <Button variant="outline" size="sm">
              Test Water Pump
            </Button>
          </div>
        </div>
      </Card>

      {/* Power Management */}
      <Card className="p-6">
        <div className="flex items-center gap-2 mb-6">
          <Battery className="w-5 h-5 text-[#4CAF50]" />
          <h3>Power Management</h3>
        </div>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="mb-1">Battery Level</p>
              <p className="text-sm text-muted-foreground">Fully charged</p>
            </div>
            <div className="text-right">
              <p>92%</p>
              <Progress value={92} className="w-24 h-2 mt-1" />
            </div>
          </div>
          <Separator />
          <div className="flex items-center justify-between">
            <div>
              <p className="mb-1">Estimated Runtime</p>
              <p className="text-sm text-muted-foreground">At current usage</p>
            </div>
            <p>6h 24m</p>
          </div>
          <Separator />
          <div className="flex items-center justify-between">
            <div>
              <p className="mb-1">Solar Charging</p>
              <p className="text-sm text-muted-foreground">Panel efficiency</p>
            </div>
            <Badge variant="outline" className="text-[#FFEB3B] border-[#FFEB3B]">
              Active (87%)
            </Badge>
          </div>
          <Separator />
          <div className="flex items-center justify-between">
            <div>
              <p className="mb-1">Power Saving Mode</p>
              <p className="text-sm text-muted-foreground">Extend battery life</p>
            </div>
            <Switch />
          </div>
        </div>
      </Card>

      {/* Automation Settings */}
      <Card className="p-6">
        <div className="flex items-center gap-2 mb-6">
          <Droplet className="w-5 h-5 text-[#4CAF50]" />
          <h3>Automation Settings</h3>
        </div>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="auto-treatment">Automatic Treatment</Label>
              <p className="text-sm text-muted-foreground">
                Apply treatments without manual approval
              </p>
            </div>
            <Switch
              id="auto-treatment"
              checked={autoTreatment}
              onCheckedChange={setAutoTreatment}
            />
          </div>
          <Separator />
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="notifications">Push Notifications</Label>
              <p className="text-sm text-muted-foreground">
                Receive alerts for detected issues
              </p>
            </div>
            <Switch
              id="notifications"
              checked={notifications}
              onCheckedChange={setNotifications}
            />
          </div>
          <Separator />
          <div className="flex items-center justify-between">
            <div>
              <Label htmlFor="night-mode">Night Mode Operation</Label>
              <p className="text-sm text-muted-foreground">
                Allow scanning during nighttime hours
              </p>
            </div>
            <Switch
              id="night-mode"
              checked={nightMode}
              onCheckedChange={setNightMode}
            />
          </div>
        </div>
      </Card>

      {/* System Actions */}
      <Card className="p-6">
        <div className="flex items-center gap-2 mb-6">
          <Zap className="w-5 h-5 text-[#FFEB3B]" />
          <h3>System Actions</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <Button variant="outline">Restart Rover</Button>
          <Button variant="outline">Clear Cache</Button>
          <Button variant="outline">Export Logs</Button>
          <Button variant="outline">Factory Reset</Button>
        </div>
      </Card>
    </div>
  );
}

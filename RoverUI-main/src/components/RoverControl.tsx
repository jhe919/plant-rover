import { useState } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Slider } from './ui/slider';
import { Badge } from './ui/badge';
import { ArrowUp, ArrowDown, ArrowLeft, ArrowRight, Circle, Play, Square, Home, Zap } from 'lucide-react';

export function RoverControl() {
  const [speed, setSpeed] = useState([50]);
  const [mode, setMode] = useState<'manual' | 'autonomous'>('manual');

  const handleMove = (direction: string) => {
    console.log(`Moving ${direction} at speed ${speed[0]}%`);
  };

  return (
    <div className="space-y-6">
      {/* Manual Control */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h3>Manual Control</h3>
          <Badge variant={mode === 'manual' ? 'default' : 'outline'} className={mode === 'manual' ? 'bg-[#4CAF50]' : ''}>
            {mode === 'manual' ? 'Active' : 'Inactive'}
          </Badge>
        </div>

        {/* Direction Pad */}
        <div className="mb-8">
          <p className="text-sm text-muted-foreground mb-4">Movement Control</p>
          <div className="grid grid-cols-3 gap-2 w-fit mx-auto">
            <div />
            <Button
              variant="outline"
              size="lg"
              className="w-16 h-16 hover:bg-[#4CAF50]/10 hover:border-[#4CAF50]"
              onClick={() => handleMove('forward')}
              disabled={mode === 'autonomous'}
            >
              <ArrowUp className="w-6 h-6" />
            </Button>
            <div />
            <Button
              variant="outline"
              size="lg"
              className="w-16 h-16 hover:bg-[#4CAF50]/10 hover:border-[#4CAF50]"
              onClick={() => handleMove('left')}
              disabled={mode === 'autonomous'}
            >
              <ArrowLeft className="w-6 h-6" />
            </Button>
            <Button
              variant="outline"
              size="lg"
              className="w-16 h-16 hover:bg-[#4CAF50]/10 hover:border-[#4CAF50]"
              onClick={() => handleMove('stop')}
              disabled={mode === 'autonomous'}
            >
              <Circle className="w-6 h-6" />
            </Button>
            <Button
              variant="outline"
              size="lg"
              className="w-16 h-16 hover:bg-[#4CAF50]/10 hover:border-[#4CAF50]"
              onClick={() => handleMove('right')}
              disabled={mode === 'autonomous'}
            >
              <ArrowRight className="w-6 h-6" />
            </Button>
            <div />
            <Button
              variant="outline"
              size="lg"
              className="w-16 h-16 hover:bg-[#4CAF50]/10 hover:border-[#4CAF50]"
              onClick={() => handleMove('backward')}
              disabled={mode === 'autonomous'}
            >
              <ArrowDown className="w-6 h-6" />
            </Button>
            <div />
          </div>
        </div>

        {/* Speed Control */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <p className="text-sm text-muted-foreground">Speed Control</p>
            <Badge variant="outline">{speed[0]}%</Badge>
          </div>
          <Slider
            value={speed}
            onValueChange={setSpeed}
            max={100}
            step={10}
            disabled={mode === 'autonomous'}
            className="mb-2"
          />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>Slow</span>
            <span>Fast</span>
          </div>
        </div>

        {/* Mode Controls */}
        <div className="space-y-3 pt-6 border-t">
          <Button
            onClick={() => setMode('autonomous')}
            className="w-full bg-[#4CAF50] hover:bg-[#45a049]"
            disabled={mode === 'autonomous'}
          >
            <Play className="w-4 h-4 mr-2" />
            Start Autonomous Mode
          </Button>
          <Button
            variant="outline"
            onClick={() => setMode('manual')}
            className="w-full"
            disabled={mode === 'manual'}
          >
            <Square className="w-4 h-4 mr-2" />
            Stop & Switch to Manual
          </Button>
          <Button variant="outline" className="w-full">
            <Home className="w-4 h-4 mr-2" />
            Return to Base
          </Button>
        </div>
      </Card>

      {/* Status & Info */}
      <Card className="p-6">
        <div className="flex items-center gap-2 mb-4">
          <Zap className="w-5 h-5 text-[#FFEB3B]" />
          <h3>Current Status</h3>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-muted-foreground mb-1">Mode</p>
            <p className="text-[#4CAF50]">{mode === 'autonomous' ? 'Autonomous' : 'Manual'}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground mb-1">Speed</p>
            <p>{speed[0]}%</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground mb-1">Position</p>
            <p>--</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground mb-1">Distance to Base</p>
            <p>--</p>
          </div>
        </div>
      </Card>
    </div>
  );
}

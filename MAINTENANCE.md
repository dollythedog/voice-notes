# Maintenance Guide

## Regular Maintenance Tasks

### Daily/Weekly
- Monitor disk space in `/srv/voice_notes/archive/`
- Check service logs: `./service_control.sh logs-recent`
- Review transcription quality in Logseq

### Monthly
- Update Python dependencies: `pip install --upgrade -r requirements.txt`
- Archive old processed files if disk space is limited
- Review OpenAI API usage and costs
- Check Whisper model updates

## Updating Dependencies

```bash
cd /srv/voice_notes
source venv/bin/activate

# Update specific package
pip install --upgrade openai-whisper

# Update all packages
pip install --upgrade -r requirements.txt

# Regenerate requirements.txt
pip freeze > requirements.txt

# Commit changes
git add requirements.txt
git commit -m "chore: update Python dependencies"
git push
```

## Service Management

### Restart Service After Updates
```bash
./service_control.sh restart
```

### Check Service Status
```bash
./service_control.sh status
systemctl status voice-transcription.service
```

### View Logs
```bash
# Live logs
./service_control.sh logs

# Recent logs
./service_control.sh logs-recent

# Full systemd logs
journalctl -u voice-transcription.service -n 100
```

## Backup Procedures

### Backup Configuration
```bash
# Backup type configs
cp -r configs/types/ ~/backups/voice_notes_configs_$(date +%Y-%m-%d)/
```

### Backup Important Audio (Optional)
```bash
# Backup specific processed audio if needed
cp -r archive/bjj/done/ ~/backups/bjj_audio_$(date +%Y-%m-%d)/
```

## Troubleshooting

### Service Won't Start
1. Check logs: `journalctl -u voice-transcription.service -n 50`
2. Verify OPENAI_API_KEY is set in service file
3. Check file permissions: `ls -la /srv/voice_notes/`
4. Test transcription manually: `./manual_test.sh`

### Transcription Failing
1. Check disk space: `df -h`
2. Verify Whisper model cache: `ls -lh ~/.cache/whisper/`
3. Test Whisper directly: `./test_whisper.py`
4. Check audio file format (should be .wav, .mp3, .m4a, .flac, .ogg)

### Summarization Failing
1. Verify OpenAI API key: `echo $OPENAI_API_KEY`
2. Check API quota/billing at platform.openai.com
3. Test summarizer: `./test_summary_generation.py`
4. Review logs for API errors

### Logseq Not Receiving Notes
1. Verify Logseq path: `ls -la /srv/logseq_graph/pages/`
2. Check type configuration: `cat configs/types/bjj.json`
3. Test file write permissions
4. Review transcription log: `tail -f logs/transcription.log`

## Upgrading Whisper Model

To switch to a different model size:

1. Edit `transcribe_service_v3.py` - change model parameter
2. Available models: tiny, base, small, medium, large
3. Test new model: `./test_whisper.py`
4. Restart service: `./service_control.sh restart`
5. Monitor performance and accuracy

Note: Larger models are more accurate but slower.

## Archive Cleanup

If archive folders get too large:

```bash
# Check archive size
du -sh archive/*/done/

# Move old files (older than 90 days) to external storage
find archive/bjj/done/ -mtime +90 -type f -exec mv {} /external/backup/ \;

# Or delete old files (BE CAREFUL!)
# find archive/bjj/done/ -mtime +180 -type f -delete
```

## Git Workflow

### Sync Changes
```bash
cd /srv/voice_notes
git pull origin main
```

### Commit Local Changes
```bash
git add .
git commit -m "fix: description of changes

Co-Authored-By: Warp <agent@warp.dev>"
git push origin main
```

### Create Feature Branch for Experiments
```bash
git checkout -b experiment/new-feature
# Make changes
git commit -am "test: trying new approach"
git push origin experiment/new-feature
```

## Monitoring API Costs

Keep track of OpenAI usage:
- Check platform.openai.com/usage
- Typical usage: ~500-1000 tokens per summary
- GPT-4o-mini is cost-effective for this use case
- Consider usage alerts in OpenAI dashboard

## Performance Tuning

### If Transcription is Too Slow
- Switch to smaller Whisper model (base or tiny)
- Use GPU if available (requires CUDA setup)
- Process files in batches during off-hours

### If Summarization is Too Slow
- Reduce transcription length (split long audio)
- Adjust summary_prompt_override to be more concise
- Consider caching summaries for similar content

## Security Best Practices

- Never commit API keys to git (already in .gitignore)
- Rotate API keys periodically
- Monitor API usage for anomalies
- Keep service file permissions restricted
- Regular security updates: `sudo apt update && sudo apt upgrade`

## Version Control

When making significant changes:
1. Update version in commit message
2. Tag releases: `git tag -a v3.1.0 -m "Version 3.1.0 - Added X feature"`
3. Push tags: `git push origin --tags`
4. Document changes in commit messages

## Support and Documentation

- Main README: README_V3.md
- Project rules: WARP.md
- Implementation history: IMPLEMENTATION_SUMMARY.md
- GitHub issues: https://github.com/dollythedog/voice-notes/issues
